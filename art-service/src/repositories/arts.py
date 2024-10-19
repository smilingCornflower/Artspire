# SQLAlchemy
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Local
from config import logger
from database.db import db_manager
from models.arts import ArtOrm
from repositories.repository import SQLAlchemyRepository
from schemas.arts import ArtCreateDTO
from schemas.tags import TagEntity

from .art_to_tag import ArtToTagRepository
from .tags import TagRepository

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy import Update, Result
    from sqlalchemy.ext.asyncio import AsyncSession


class ArtRepository(SQLAlchemyRepository):
    model = ArtOrm

    async def change_counter(self, art_id: int, number: int, counter_name: str):
        # noinspection PyTypeChecker
        stmt: "Update" = update(self.model).where(self.model.id == art_id)
        if counter_name == "likes":
            stmt: "Update" = stmt.values(likes_count=self.model.likes_count + number)
        elif counter_name == "views":
            stmt: "Update" = stmt.values(views_count=self.model.views_count + number)
        else:
            raise ValueError(f"Invalid counter name: {counter_name}")
        async with self.transaction():
            result: "Result" = await self._session.execute(stmt)
        return result.rowcount
