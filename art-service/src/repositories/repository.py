from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from database.db import db_manager
from sqlalchemy import insert, select, and_
from config import settings, logger
from schemas.entities import BaseEntity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

if TYPE_CHECKING:
    from sqlalchemy import (
        Insert, Select, ChunkedIteratorResult
    )
    from schemas.arts import ArtCreateSchema
    from sqlalchemy.orm import DeclarativeMeta
    from sqlalchemy.sql.expression import BinaryExpression
    from sqlalchemy.sql.schema import Column


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
                logger.warning(f"Started inserting into model: {self.model}")
                logger.debug(f"Model: {self.model} data to be inserted: {data}")
                try:

                    stmt: "Insert" = insert(self.model).values(**data).returning(self.model.id)
                    logger.debug(f"SQL statement: {stmt}")

                    result: "ChunkedIteratorResult" = await session.execute(stmt)
                    logger.debug(f"Execution result: {result}")

                    result_id: int = result.scalar_one()
                    logger.debug(f"Inserted record ID: {result_id}")
                    return result_id
                except IntegrityError as err:
                    logger.error(f"IntegrityError occurred: {err}")
                    raise err

                except SQLAlchemyError as err:
                    logger.error(f"SQLAlchemyError occurred: {err}")
                    raise err

    async def find_all(self, filter_by: dict) -> "list[BaseEntity]":
        async with db_manager.async_session_maker() as session:
            logger.warning(f"Started filtering in model: {self.model}")
            logger.debug(f"Filter criteria: {filter_by}")

            stmt: "Select" = select(self.model)
            if filter_by:
                conditions: list[BinaryExpression] = []
                value: "Column"
                for key, value in filter_by.items():
                    if hasattr(self.model, key):
                        expression: "BinaryExpression" = getattr(self.model, key) == value
                        logger.debug(f"expression: {expression} for key: {key} with value: {value}")
                        conditions.append(expression)
                if conditions:
                    stmt = stmt.where(and_(*conditions))
                    logger.debug(f"Updated SQL statement with filters: {stmt}")
            try:
                result: "ChunkedIteratorResult" = await session.execute(stmt)
                logger.debug(f"Query execution result: {result}")

                rows = result.all()
                logger.debug(f"Rows fetched: {rows}")

                entities: "list[BaseEntity]" = [row[0].to_entity() for row in rows]
                logger.debug(f"Entities converted: {entities}")
                return entities
            except SQLAlchemyError as err:
                logger.error(f"SQLAlchemyError occurred during filtering: {err}")
                raise err
