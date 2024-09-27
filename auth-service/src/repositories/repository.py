from abc import ABC, abstractmethod
from sqlalchemy import insert, select, and_
from database.db import db_manager
from config import settings, logger

# Annotation
from sqlalchemy import Select, Insert, ChunkedIteratorResult
from sqlalchemy.sql.expression import BinaryExpression
from sqlalchemy.orm import DeclarativeMeta


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
                logger.debug(f"Executing insert for {self.model.__name__} with data: {data}")
                result: ChunkedIteratorResult = await session.execute(stmt)
                new_id: int = result.scalar_one()
                logger.info(f"Successfully added {self.model.__name__} with id: {new_id}")
                return new_id

    async def find_all(self, filter_by: dict = None) -> list:
        async with db_manager.async_session_maker() as session:
            stmt: Select = select(self.model)
            if filter_by:
                conditions: list[BinaryExpression] = []
                logger.debug(f"Filtering {self.model.__name__} with conditions: {filter_by}")
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

            result: ChunkedIteratorResult = await session.execute(stmt)
            entities: list = [row[0].to_entity() for row in result.all()]
            logger.info(f"Retrieved {len(entities)} records from {self.model.__name__}")
            return entities
