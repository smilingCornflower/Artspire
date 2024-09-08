from typing import TYPE_CHECKING

from sqlalchemy.exc import SQLAlchemyError
from repositories.arts import ArtRepository
from config import logger
from exceptions.http_exc import (
    InternalServerErrorHTTPException,
    ArtAlreadySavedHTTPException,
    ArtNotFoundHTTPException,
)

if TYPE_CHECKING:
    from repositories.user_saved_arts import UserSavedArtsRepository
    from schemas.entities import UserSavedArtsEntity


class UserSavedArtsService:
    arts_repo: "ArtRepository" = ArtRepository()

    def __init__(self, user_saved_repo: "UserSavedArtsRepository"):
        self.user_saved_repo = user_saved_repo

    async def add_to_saved(self, user_id: int, art_id: int) -> bool:
        logger.warning(f"Started saving art")
        art_with_this_id: list = await self.arts_repo.find_all({"id": art_id})
        if not art_with_this_id:
            logger.warning(f"Art {art_id} not found")
            raise ArtNotFoundHTTPException

        user_saved_arts: list = await self.user_saved_repo.find_all({"id": user_id})
        if user_saved_arts:
            user_saved_arts: "UserSavedArtsEntity" = user_saved_arts[0]

            if art_id in user_saved_arts.arts:
                logger.info(f"Art {art_id} already saved for user {user_id}")
                raise ArtAlreadySavedHTTPException

            user_saved_arts.arts.append(art_id)
            to_update: dict = {"arts": user_saved_arts.arts}
            try:
                await self.user_saved_repo.update_one(model_id=user_id, data=to_update)
                logger.info(f"Updated saved arts for user {user_id}")
            except SQLAlchemyError as err:
                logger.error(f"Failed to update saved arts for user {user_id}: {err}")
                raise InternalServerErrorHTTPException
        else:
            to_add: dict = {"id": user_id, "arts": [art_id]}
            try:
                await self.user_saved_repo.add_one(to_add)
                logger.info(f"Added new saved arts for user {user_id}")
            except SQLAlchemyError as err:
                logger.error(f"Failed to add saved arts for user {user_id}: {err}")
                raise InternalServerErrorHTTPException
        return True
