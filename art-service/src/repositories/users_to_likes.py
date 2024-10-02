from typing import TYPE_CHECKING
from .repository import SQLAlchemyRepository
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Result
from models.users_to_likes import UsersToLikesOrm

from config import logger

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

