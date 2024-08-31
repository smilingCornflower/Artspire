from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from sqlalchemy import insert, select, delete, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from config import logger
from database.db import db_manager
from schemas.entities import BaseEntity

if TYPE_CHECKING:
    from sqlalchemy import Insert, Select, Delete, ChunkedIteratorResult
    from sqlalchemy.orm import DeclarativeMeta
    from sqlalchemy.sql.expression import BinaryExpression
    from sqlalchemy.sql.schema import Column
    from schemas.arts import ArtCreateSchema


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data):
        raise NotImplemented

    @abstractmethod
    async def find_all(self, data):
        raise NotImplemented


class SQLAlchemyRepository(AbstractRepository):
    model: "DeclarativeMeta" = None

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
                for key, value in filter_by.items():
                    if hasattr(self.model, key):
                        expression: "BinaryExpression" = getattr(self.model, key) == value
                        logger.debug(f"Expression: {expression} for key: {key} with value: {value}")
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

    async def delete_one(self, item_id: int) -> bool:
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                try:
                    stmt: "Delete" = delete(self.model).where(self.model.id == item_id)
                    result: "ChunkedIteratorResult" = await session.execute(stmt)

                    if result.rowcount == 1:
                        logger.info(f"Successfully deleted item with ID {item_id}.")
                        return True
                    else:
                        logger.warning(f"Item with ID {item_id} not found or already deleted.")
                        return False
                except SQLAlchemyError as err:
                    logger.error(f"Error occurred during delete operation: {err}", exc_info=True)
                    raise err
