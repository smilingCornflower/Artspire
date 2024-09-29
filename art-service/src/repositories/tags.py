from database.db import db_manager
from .repository import SQLAlchemyRepository
from models.tags import TagOrm
from typing import TYPE_CHECKING
from config import logger
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

if TYPE_CHECKING:
    from sqlalchemy import Select, Result
    from schemas.entities import TagEntity


class TagRepository(SQLAlchemyRepository):
    model = TagOrm

    async def get_tags_by_name_part(self, tag_part: str) -> list["TagEntity"]:
        logger.debug(f"Selecting from {self.model.__name__} with tag_part: {tag_part}")
        async with db_manager.async_session_maker() as session:
            tag_part: str = tag_part + "%"
            stmt: "Select" = (
                select(self.model)
                .filter(func.lower(self.model.name)
                        .like(tag_part)
                        )
            )

            try:
                result: "Result" = await session.execute(stmt)
            except SQLAlchemyError as err:
                logger.error(f"SQLAlchemyError: {err}")
                raise err
            rows = result.all()

            entities: "list[TagEntity]" = [row[0].to_entity() for row in rows]
            logger.info(f"Found {len(entities)} entities")
            return entities
