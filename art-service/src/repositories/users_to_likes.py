from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import insert

from config import logger
from models.users_to_likes import UsersToLikesOrm
from .repository import SQLAlchemyRepository

if TYPE_CHECKING:
    from sqlalchemy.dialects.postgresql import Insert
    from sqlalchemy import Result


class UsersToLikesRepository(SQLAlchemyRepository):
    model = UsersToLikesOrm

    async def add_one(self, data: dict) -> int:
        logger.debug(f"STARTED add_one()")
        stmt: "Insert" = insert(self.model).values(**data)
        stmt: "Insert" = stmt.on_conflict_do_nothing(index_elements=["user_id", "art_id"])
        async with self.transaction():
            result: "Result" = await self._session.execute(stmt)
        return result.rowcount

