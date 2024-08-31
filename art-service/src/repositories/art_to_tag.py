from typing import TYPE_CHECKING

from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError

from config import logger
from database.db import db_manager
from models.art_to_tag import art_to_tag
from .repository import SQLAlchemyRepository

if TYPE_CHECKING:
    from sqlalchemy import Insert


class ArtToTagRepository(SQLAlchemyRepository):
    model = art_to_tag

    async def add_one(self, data: dict) -> None:
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                logger.warning(f"Started inserting into model: {self.model}")
                logger.debug(f"Model: {self.model}, data to be inserted: {data}")
                try:
                    stmt: "Insert" = insert(self.model).values(**data)
                    logger.debug(f"SQL statement: {stmt}")

                    await session.execute(stmt)

                except SQLAlchemyError as err:
                    logger.error(f"SQLAlchemyError occurred: {err}")
                    raise err
