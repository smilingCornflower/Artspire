from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from database.db import db_manager
from sqlalchemy import insert, select, and_
from config import settings, logger
from schemas.entities import BaseEntity

if TYPE_CHECKING:
    from sqlalchemy import (
        Insert, Select, ChunkedIteratorResult
    )
    from sqlalchemy.orm import DeclarativeMeta
    from sqlalchemy.sql.expression import BinaryExpression


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data):
        raise NotImplemented

    @abstractmethod
    async def find_all(self, data):
        raise NotImplemented


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict) -> int:
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                logger.warning(f"Started inserting in {self.model}")
                logger.debug(f"Model: {self.model} data: {data}")

                stmt: "Insert" = insert(self.model).values(**data).returning(self.model.id)
                result: "ChunkedIteratorResult" = await session.execute(stmt)
                result: int = result.scalar_one()
                logger.debug(f"result: {repr(result)}")
                return result

    async def find_all(self, filter_by: dict) -> "list[BaseEntity]":
        async with db_manager.async_session_maker() as session:
            logger.warning(f"Started filtering in {self.model}")

            stmt: "Select" = select(self.model)
            if filter_by:
                conditions: list[BinaryExpression] = []
                for key, value in filter_by.items():
                    if hasattr(self.model, key):
                        # noinspection PyTypeChecker
                        expression: "BinaryExpression" = self.mode.key == value
                        logger.debug(f"expression type: {type(expression)}\n\t value: {repr(expression)}")
                        conditions.append(expression)
                if conditions:
                    stmt: "Select" = stmt.where(and_(*conditions))
                result: "ChunkedIteratorResult" = session.execute(stmt)
                result: "list[BaseEntity]" = [row[0].to_entity() for row in result.all()]
                return result
