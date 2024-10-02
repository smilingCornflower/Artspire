# Standard libraries
from typing import TYPE_CHECKING

# SQLAlchemy
from sqlalchemy import insert

# Local
from config import logger
from models.art_to_tag import art_to_tag
from .repository import SQLAlchemyRepository

# Type hints
if TYPE_CHECKING:
    from sqlalchemy import Insert


class ArtToTagRepository(SQLAlchemyRepository):
    model = art_to_tag

    async def add_one(self, data: dict | list[dict]) -> None:
        logger.warning("STARTED add_one()")
        stmt: "Insert" = insert(self.model).values(data)
        logger.debug(f"stmt: \n{stmt}")
        async with self.transaction():
            await self._session.execute(stmt)
            logger.info("FINISHED add_one()")