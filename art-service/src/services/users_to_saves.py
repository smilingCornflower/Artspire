from typing import TYPE_CHECKING
from exceptions.http_exc import ArtNotFoundHTTPException, InternalServerErrorHTTPException

from sqlalchemy.exc import SQLAlchemyError
from config import logger


if TYPE_CHECKING:
    from repositories.users_to_saves import UsersToSavesRepository
    from repositories.arts import ArtRepository
    from repositories.tags import TagRepository
    from repositories.art_to_tag import ArtToTagRepository
    from schemas.entities import UsersToSavesEntity
    from schemas.arts import ArtEntity


class UsersToSavesService:
    def __init__(self,
                 users_to_saves_repo: "UsersToSavesRepository",
                 art_repo: "ArtRepository",
                 ):
        self.repo: "UsersToSavesRepository" = users_to_saves_repo
        self.art_repo: "ArtRepository" = art_repo

    async def save_art(self, user_id: int, art_id: int) -> bool:
        """
        Saves a pair (user_id, art_id) in users_to_saves in repository.

        :param user_id: The ID of the user.
        :param art_id: The ID of the art.
        :return: True if record has written, False if such pair already exists in repository
        :raises ArtNotFoundHTTPException: If the art with the given art_id is not found.
        :raises InternalServerErrorHTTPException: If an error occurs while adding the record to the repository.
        """
        logger.warning(f"STARTED save_art()")
        logger.debug(f"(user_id, art_id) = ({user_id}, {art_id})")
        # noinspection PyTypeChecker
        seeking_result: "list[ArtEntity]" = await self.art_repo.find_all({"id": art_id})
        if not seeking_result:
            raise ArtNotFoundHTTPException(f"Art with id: {art_id} not found")

        to_add: dict = {"user_id": user_id, "art_id": art_id}
        try:
            result_rowcount: int = await self.repo.add_one(data=to_add)
            logger.info(f"Finished save_art(), rowcount={result_rowcount}")
        except SQLAlchemyError as err:
            raise InternalServerErrorHTTPException from err
        return bool(result_rowcount)

    async def get_saved_arts(self,
                             user_id: int,
                             offset: int | None = None,
                             limit: int | None = None,
                             include_tags: bool = False
                             ) -> list["ArtEntity"]:

        try:
            # noinspection PyTypeChecker
            saved_arts: list["UsersToSavesEntity"] = await self.repo.find_all(
                filter_by={"user_id": user_id},
                offset=offset,
                limit=limit,
            )
            if not saved_arts:
                logger.info(f"saved_arts is empty -> return []")
                return []
            saved_arts_id: list = [i.art_id for i in saved_arts]
            art_attributes: list[str] | None = None
            if include_tags:
                art_attributes = ["tags"]
            # noinspection PyTypeChecker
            result_arts: list["ArtEntity"] = await self.art_repo.find_all(
                filter_by={"id": saved_arts_id},
                joined_attributes=art_attributes,
            )
        except SQLAlchemyError as err:
            logger.error(f"Error: {err}")
            raise InternalServerErrorHTTPException from err
        return result_arts

    async def delete_from_saved(self, user_id: int, art_id: int) -> bool:
        """
        Delete the record from users_to_saves from repository
        @return: True or False. True if an item was deleted, False if it was not found in repository
        """
        logger.info(f"Started delete_from_saved()")
        to_delete: dict = {"user_id": user_id, "art_id": art_id}
        logger.debug(f"to_delete: {to_delete}")
        result_rows: int = await self.repo.delete_one(to_delete)
        return bool(result_rows)
