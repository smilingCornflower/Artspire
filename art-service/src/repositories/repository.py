# Standard lib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# SQLAlchemy
from sqlalchemy import insert, select, update, delete, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Local
from config import logger
from database.db import db_manager
from schemas.entities import BaseEntity

# Type hints
if TYPE_CHECKING:
    from sqlalchemy import (
        Insert, Select, Delete, Update, ChunkedIteratorResult)
    from sqlalchemy.orm import DeclarativeMeta
    from sqlalchemy.sql.expression import BinaryExpression
    from sqlalchemy.sql.schema import Column
    from schemas.arts import ArtCreateSchema


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplemented

    @abstractmethod
    async def find_all(self, filter_by: dict):
        raise NotImplemented

    @abstractmethod
    async def update_one(self, model_id: int, data: dict):
        raise NotImplemented

    @abstractmethod
    async def delete_one(self, object_id: int):
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
            logger.debug(f"Select statement: {stmt}")
            if filter_by:
                conditions: list[BinaryExpression] = []
                for key, value in filter_by.items():
                    if hasattr(self.model, key):
                        # noinspection PyTypeChecker
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

                entities: "list[BaseEntity]" = [row[0].to_entity() for row in rows]
                logger.debug(f"Entities converted: {entities}")
                return entities
            except SQLAlchemyError as err:
                logger.error(f"SQLAlchemyError occurred during filtering: {err}")
                raise err

    async def delete_one(self, object_id: int) -> bool:
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                try:
                    stmt: "Delete" = delete(self.model).where(self.model.id == object_id)
                    result: "ChunkedIteratorResult" = await session.execute(stmt)

                    if result.rowcount == 1:
                        logger.info(f"Successfully deleted item with ID {object_id}.")
                        return True
                    else:
                        logger.warning(f"Item with ID {object_id} not found or already deleted.")
                        return False
                except SQLAlchemyError as err:
                    logger.error(f"Error occurred during delete operation: {err}", exc_info=True)
                    raise err

    async def update_one(self, model_id: int, data: dict):
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                try:
                    logger.info(f"Started updating model with id: {model_id}")

                    stmt = update(self.model).where(self.model.id == model_id).values(**data)
                    logger.debug(f"Update statement: {stmt}")

                    await session.execute(stmt)
                    logger.info(f"Update successful for model_id: {model_id}")

                except SQLAlchemyError as err:
                    logger.error(
                        f"SQLAlchemyError occurred while updating model_id: {model_id}. Error: {err}")
                    raise err
