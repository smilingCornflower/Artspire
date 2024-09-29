from repositories.comments import CommentsRepository
from repositories.arts import ArtRepository
from schemas.comments import CommentCreateSchema, CommentEntity, CommentOutSchema
from schemas.entities import UserEntity
from sqlalchemy.exc import SQLAlchemyError
from config import logger
from rabbit.users_client import run_users_client


from exceptions.http_exc import (
    InternalServerErrorHTTPException,
    ArtNotFoundHTTPException,
    CommentLengthHTTPException,
)


class CommentsService:
    def __init__(
            self,
            comments_repo: "CommentsRepository",
            art_repo: "ArtRepository",
    ):
        self.repo = comments_repo
        self.art_repo = art_repo

    async def add_comment(self,
                          comment_create_data: "CommentCreateSchema",
                          ) -> int:
        """
        Adds a new comment for a specified art.

        This method validates the length of the comment text and checks if the
        art associated with the comment exists in the repository. If the
        comment is valid, it is added to the database.

        :param comment_create_data: The data schema containing the comment text and associated art ID.
        :return: The ID of the newly created comment record in the database.
        :raises CommentLengthHTTPException: If the comment text is empty or exceeds the allowed length of 512 characters.
        :raises ArtNotFoundHTTPException: If the art with the specified ID is not found in the repository.
        :raises InternalServerErrorHTTPException: If a database error occurs while attempting to add the comment.
        """

        if not 0 < len(comment_create_data.text) <= 512:
            logger.error(f"Comment length error")
            raise CommentLengthHTTPException

        logger.info(f"Adding comment for art_id: {comment_create_data.art_id}")

        result_art: list = await self.art_repo.find_all({"id": comment_create_data.art_id})
        if not result_art:
            logger.warning(f"Art with id {comment_create_data.art_id} not found")
            raise ArtNotFoundHTTPException

        try:
            result: int = await self.repo.add_one(data=comment_create_data.model_dump())
            logger.info(f"Comment added successfully with id: {result}")
        except SQLAlchemyError as err:
            logger.critical(f"Database error while adding comment: {err}")
            raise InternalServerErrorHTTPException("Failed to publish the comment") from err

        return result

    async def get_comments(self,
                           art_id: int,
                           offset: int | None = None,
                           limit: int | None = None,
                           ) -> list:
        """
        Retrieve comments associated with a specific art piece.

        This method fetches comments from the repository based on the provided art ID.
        It supports pagination via the `offset` and `limit` parameters.

        :param art_id: The ID of the art piece for which comments are being retrieved.
        :param offset: The number of comments to skip before starting to collect the result set (optional).
        :param limit: The maximum number of comments to return (optional).
        :return: A list of CommentOutSchema objects containing full information about each comment.
        :raises InternalServerErrorHTTPException: If an error occurs while retrieving comments from the database.
        """

        logger.info(f"Fetching comments; art_id={art_id} with offset={offset} and limit={limit}")
        try:
            # noinspection PyTypeChecker
            result_comments: list["CommentEntity"] = await self.repo.find_all(
                filter_by={"art_id": art_id},
                offset=offset,
                limit=limit,
            )
            logger.info(f"Retrieved {len(result_comments)} comments for art_id={art_id}.")
            users_id: list = [comment.user_id for comment in result_comments]

            # !! The result user_entities ignores duplicates of user_id
            user_entities: dict[int, "UserEntity"] = await run_users_client(users_id=users_id)
            logger.debug(f"Retrieved user entities for {len(user_entities)} users.")

        except SQLAlchemyError as err:
            logger.error(f"Error while fetching comments for art_id={art_id}: {err}")
            raise InternalServerErrorHTTPException from err

        result: list = []

        for comment in result_comments:
            user: "UserEntity" = user_entities[comment.user_id]
            comment_out: "CommentOutSchema" = CommentOutSchema(
                id=comment.id,
                user_id=comment.user_id,
                user_username=user.username,
                user_profile_image=user.profile_image,
                text=comment.text,
                likes_count=comment.likes_count,
                dislikes_count=comment.dislikes_count,
                is_edited=comment.is_edited,
                created_at=comment.created_at
            )
            result.append(comment_out)

        logger.info(f"Returning {len(result)} comments for art_id={art_id}.")
        return result
