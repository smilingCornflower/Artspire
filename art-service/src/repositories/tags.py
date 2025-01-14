from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as psql_insert

from config import logger
from models.tags import TagOrm
from .repository import SQLAlchemyRepository

if TYPE_CHECKING:
    from sqlalchemy import Select, Result
    from schemas.tags import TagEntity
    from sqlalchemy.dialects.postgresql import Insert as PsqlInsert


class TagRepository(SQLAlchemyRepository):
    model = TagOrm

    async def add_one(self, data: dict | list[dict], ignore_conflicts: list[str] = None) -> None:
        logger.info(f"STARTED add_one()")
        stmt: "PsqlInsert" = psql_insert(self.model).values(data)
        stmt = stmt.on_conflict_do_nothing(index_elements=ignore_conflicts)

        logger.debug(f"stmt: \n{stmt}")
        async with self.transaction():
            await self._session.execute(stmt)

    async def get_tags_by_name_part(self, tag_part: str) -> list["TagEntity"]:
        logger.warning(f"STARTED get_tags_by_name_part()")
        tag_part: str = tag_part.lower() + "%"
        stmt: "Select" = select(self.model).filter(
            func.lower(self.model.name).like(tag_part)
        )

        result: "Result" = await self._session.execute(stmt)
        rows = result.all()

        entities: "list[TagEntity]" = [row[0].to_entity() for row in rows]
        logger.info(f"Found {len(entities)} entities")
        return entities
