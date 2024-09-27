from repositories.comments import CommentsRepository
from repositories.arts import ArtRepository
from schemas.comments import CommentCreateSchema
from sqlalchemy.exc import SQLAlchemyError
from config import logger
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
