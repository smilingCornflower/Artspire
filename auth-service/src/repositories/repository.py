from abc import ABC, abstractmethod
from sqlalchemy import insert, select, and_
from database.db import db_manager
from config import settings
from schemas.users import UserEntity

# Annotation
from sqlalchemy import Select, Insert, ChunkedIteratorResult
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.orm import DeclarativeMeta

# Logging
from loguru import logger

logger.add(settings.logs_path,
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{file} | {function} | {line}] \n \t {message}",
           level="DEBUG",
           rotation="10 MB",
           compression="zip")


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data):
        raise NotImplemented

    @abstractmethod
    async def find_all(self, filter_by):
        raise NotImplemented


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def add_one(self, data: dict) -> int:
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                stmt: Insert = insert(self.model).values(**data).returning(self.model.id)
                result: ChunkedIteratorResult = await session.execute(stmt)
                result: DeclarativeMeta = result.scalar_one()
                return result

    async def find_all(self, filter_by: dict = None) -> list:
        async with db_manager.async_session_maker() as session:
            stmt: Select = select(self.model)
            if filter_by:
                conditions: list[BinaryExpression] = [
                    getattr(self.model, key) == value for key, value in filter_by.items()
                ]
                if conditions:
                    stmt: Select = stmt.where(and_(*conditions))

            result: ChunkedIteratorResult = await session.execute(stmt)
            result: list = [row[0].to_entity() for row in result.all()]
            return result
