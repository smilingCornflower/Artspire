from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import insert

from config import logger
from models.users_to_saves import UsersToSavesOrm
from .repository import SQLAlchemyRepository

if TYPE_CHECKING:
    from sqlalchemy.dialects.postgresql import Insert
    from sqlalchemy import Result


class UsersToSavesRepository(SQLAlchemyRepository):
    model = UsersToSavesOrm

    async def add_one(self, data: dict) -> int:
        logger.debug(f"Insert data: {data}")
        stmt: "Insert" = insert(self.model).values(**data)
        stmt: "Insert" = stmt.on_conflict_do_nothing(
            index_elements=["user_id", "art_id"]
        )
        async with self.transaction():
            result: "Result" = await self._session.execute(stmt)
        return result.rowcount