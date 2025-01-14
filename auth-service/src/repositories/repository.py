from abc import ABC, abstractmethod

# Annotation
from sqlalchemy import and_, ChunkedIteratorResult, delete, Delete, insert, Insert, Result, select, \
    Select, update
from sqlalchemy.sql.expression import BinaryExpression

from config import logger
from database.db import db_manager


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, filter_by):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, delete_by):
        raise NotImplementedError


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
                            expression: BinaryExpression = getattr(self.model, key).in_(value)
                        else:
                            # noinspection PyTypeChecker
                            expression: BinaryExpression = getattr(self.model, key) == value
                        conditions.append(expression)
                if conditions:
                    stmt = stmt.where(and_(*conditions))

            result: ChunkedIteratorResult = await session.execute(stmt)
            entities: list = [row[0].to_entity() for row in result.all()]
            logger.info(f"Retrieved {len(entities)} records from {self.model.__name__}")
            return entities

    async def delete_one(self, delete_by: dict) -> bool:
        logger.warning(f"STARTED delete_one({delete_by})")
        conditions: list[BinaryExpression] = []
        for key, value in delete_by.items():
            if not hasattr(self.model, key):
                raise AttributeError(f"A model {self.model} has no attribute {key}")
            # noinspection PyTypeChecker
            expression: BinaryExpression = getattr(self.model, key) == value
            conditions.append(expression)
        if not conditions:
            raise ValueError(f"Conditions must contain at least one entry")

        async with db_manager.async_session_maker() as session:
            async with session.begin():
                stmt: Delete = delete(self.model).where(and_(*conditions))
                result: Result = await session.execute(stmt)

                if result.rowcount == 1:
                    logger.info(
                        f"SUCCESS: Deleted a record in {self.model.__name__} matching {delete_by}")

                    return True
                elif result.rowcount == 0:
                    logger.warning(
                        f"No records found in {self.model.__name__} matching {delete_by}")

                    return False
                else:
                    session.rollback()
                    logger.critical(
                        f"ROLLBACK: delete_one() affected more than one row for {delete_by}")
                    return False

    async def update_one(self, model_id: int, data: dict) -> None:
        logger.warning(f"STARTED update_one()")
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                stmt = update(self.model).where(self.model.id == model_id).values(data)
                await session.execute(stmt)
