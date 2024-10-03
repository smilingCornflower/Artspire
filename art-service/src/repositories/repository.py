# Standard lib
from __future__ import annotations
from contextlib import asynccontextmanager
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# SQLAlchemy
from sqlalchemy import insert, select, update, delete, and_
from sqlalchemy.orm import joinedload

# Local
from config import logger
from schemas.entities import BaseEntity

# Type hints
if TYPE_CHECKING:
    from sqlalchemy import Insert, Select, Delete, Result
    from sqlalchemy.orm import DeclarativeMeta
    from sqlalchemy.sql.expression import BinaryExpression
    from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_all(
        self,
        filter_by: dict,
        offset: int | None,
        limit: int | None,
    ):
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, model_id: int, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, delete_by: dict):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model: "DeclarativeMeta" = None

    def __init__(self, session: "AsyncSession"):
        self._session: "AsyncSession" = session

    @asynccontextmanager
    async def transaction(self):
        try:
            yield
            await self._session.commit()
        except Exception as err:
            logger.critical(f"Error: {err}")
            await self._session.rollback()
            raise

    async def add_one(self, data: dict | list[dict]) -> int:
        logger.warning("STARTED add_one()")

        # TODO: Returning self.model instead of self.model.id
        stmt: "Insert" = insert(self.model).values(data).returning(self.model.id)
        logger.debug(f"stmt: \n{stmt}")

        async with self.transaction():
            result: "Result" = await self._session.execute(stmt)
        result_id: int = result.scalar_one()

        return result_id

    async def find_all(
        self,
        filter_by: dict,
        offset: int = None,
        limit: int = None,
        joined_attributes: list[str] = None,
    ) -> "list[BaseEntity]":
        logger.warning("STARTED find_all()")

        stmt: "Select" = select(self.model)
        if joined_attributes:
            for attr in joined_attributes:
                stmt: "Select" = stmt.options(joinedload(getattr(self.model, attr)))
        if offset is not None and limit is not None:
            stmt: "Select" = stmt.offset(offset).limit(limit)

        conditions: list[BinaryExpression] = []
        for key, value in filter_by.items():
            if isinstance(value, list):
                expression: "BinaryExpression" = getattr(self.model, key).in_(value)
            else:
                # noinspection PyTypeChecker
                expression: "BinaryExpression" = value == getattr(self.model, key)
            conditions.append(expression)
        if conditions:
            stmt = stmt.where(and_(*conditions))

        logger.debug(f"stmt: \n{stmt}")
        result: "Result" = await self._session.execute(stmt)
        rows = result.unique().scalars()
        entities: "list[BaseEntity]" = [row.to_entity() for row in rows]

        logger.info(f"Found {len(entities)} entities")
        return entities

    async def delete_one(self, delete_by: dict) -> int:
        logger.warning("STARTED delete_one()")
        logger.debug(f"delete_by: {delete_by}")

        conditions: list[BinaryExpression] = []
        for key, value in delete_by.items():
            if not hasattr(self.model, key):
                raise AttributeError(f"A model {self.model} has no attribute {key}")
            # noinspection PyTypeChecker
            expression: "BinaryExpression" = getattr(self.model, key) == value
            conditions.append(expression)
        if not conditions:
            raise ValueError(f"Conditions must contain at least one entry")

        stmt: "Delete" = delete(self.model).where(and_(*conditions))
        logger.debug(f"stmt: \n{stmt}")

        async with self.transaction():
            result: "Result" = await self._session.execute(stmt)
        result_rowcount: int = result.rowcount

        logger.info(f"Deleted {result_rowcount} items")
        return result_rowcount

    async def update_one(self, model_id: int, data: dict) -> None:
        logger.warning(f"STARTED update_one()")
        stmt = update(self.model).where(self.model.id == model_id).values(data)
        async with self.transaction():
            await self._session.execute(stmt)
