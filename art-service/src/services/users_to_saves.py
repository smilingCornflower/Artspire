from typing import TYPE_CHECKING
from exceptions.http_exc import ArtNotFoundHTTPException, InternalServerErrorHTTPException

from sqlalchemy.exc import SQLAlchemyError
from config import logger

if TYPE_CHECKING:
    from repositories.users_to_saves import UsersToSavesRepository
    from repositories.arts import ArtRepository
    from schemas.entities import ArtEntity


class UsersToSavesService:
    def __init__(self,
                 users_to_service_repo: "UsersToSavesRepository",
                 art_repo: "ArtRepository",
                 ):
        self.repo: "UsersToSavesRepository" = users_to_service_repo
        self.art_repo: "ArtRepository" = art_repo

    async def save_art(self, user_id: int, art_id: int) -> int:
        logger.warning(f"Started save_art()")
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
            raise InternalServerErrorHTTPException
        return result_rowcount
