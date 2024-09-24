# Standard lib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# SQLAlchemy
from sqlalchemy import insert, select, update, delete, and_
from sqlalchemy.orm import joinedload
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
    from typing import Any


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplemented

    @abstractmethod
    async def find_all(self,
                       filter_by: dict,
                       offset: int | None,
                       limit: int | None,
                       ):
        raise NotImplemented

    @abstractmethod
    async def update_one(self, model_id: int, data: dict):
        raise NotImplemented

    @abstractmethod
    async def delete_one(self, delete_by: dict):
        raise NotImplemented


class SQLAlchemyRepository(AbstractRepository):
    model: "DeclarativeMeta" = None

    async def add_one(self, data: dict) -> int:
        logger.debug(f"Insert into {self.model.__name__}: {data}")
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                try:
                    stmt: "Insert" = insert(self.model).values(**data).returning(self.model.id)
                    result: "ChunkedIteratorResult" = await session.execute(stmt)
                    result_id: int = result.scalar_one()
                    logger.info(f"Inserted ID: {result_id}")
                    return result_id
                except IntegrityError as err:
                    logger.error(f"IntegrityError: {err}")
                    raise err
                except SQLAlchemyError as err:
                    logger.error(f"SQLAlchemyError: {err}")
                    raise err

    async def find_all(self,
                       filter_by: dict,
                       offset: int = None,
                       limit: int = None,
                       joined_attributes: list[str] = None,
                       ) -> "list[BaseEntity]":
        logger.debug(f"Selecting from {self.model.__name__} with filter: {filter_by}")
        async with db_manager.async_session_maker() as session:
            stmt: "Select" = select(self.model)
            if joined_attributes:
                for attr in joined_attributes:
                    stmt: "Select" = stmt.options(joinedload(getattr(self.model, attr)))
            logger.debug(f"stmt: {stmt}")
            logger.debug(f"offset: {offset}, limit: {limit}")
            if offset is not None and limit is not None:
                stmt: "Select" = stmt.offset(offset).limit(limit)

            if filter_by:
                conditions: list[BinaryExpression] = []
                for key, value in filter_by.items():
                    if hasattr(self.model, key):
                        if isinstance(value, list):
                            expression: "BinaryExpression" = getattr(self.model, key).in_(value)
                        else:
                            # noinspection PyTypeChecker
                            expression: "BinaryExpression" = getattr(self.model, key) == value
                        conditions.append(expression)
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            try:
                result: "ChunkedIteratorResult" = await session.execute(stmt)
            except SQLAlchemyError as err:
                logger.error(f"SQLAlchemyError: {err}")
                raise err
            rows = result.unique().all()
            entities: "list[BaseEntity]" = [row[0].to_entity() for row in rows]
            logger.info(f"Found {len(entities)} entities")
            return entities

    async def delete_one(self, delete_by: dict) -> int:
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                logger.debug(f"data: {delete_by}")
                conditions: list[BinaryExpression] = []

                for key, value in delete_by.items():
                    if not hasattr(self.model, key):
                        raise AttributeError(f"A model {self.model} has no attribute {key}")
                    # noinspection PyTypeChecker
                    expression: "BinaryExpression" = getattr(self.model, key) == value
                    conditions.append(expression)
                if not conditions:
                    raise ValueError(f"Conditions must contain at least one entry")

                try:
                    stmt: "Delete" = delete(self.model).where(and_(*conditions))
                    result: "ChunkedIteratorResult" = await session.execute(stmt)
                    result_rowcount: int = result.rowcount
                    logger.info(f"Deleted {result_rowcount} items")
                    return result_rowcount
                except SQLAlchemyError as err:
                    logger.error(f"Error occurred during delete operation: {err}", exc_info=True)
                    raise err

    async def update_one(self, model_id: int, data: dict):
        logger.debug(f"Updating {self.model.__name__} with ID {model_id}")
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                try:
                    stmt = update(self.model).where(self.model.id == model_id).values(**data)
                    await session.execute(stmt)
                    logger.info(f"Updated {self.model.__name__} with ID {model_id}")
                except SQLAlchemyError as err:
                    logger.error("SQLAlchemyError during update")
                    raise err

