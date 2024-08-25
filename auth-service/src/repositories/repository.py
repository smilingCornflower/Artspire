from abc import ABC, abstractmethod
from sqlalchemy import insert, select, and_
from database.db import db_manager

from schemas.users import UserEntity


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
                stmt = insert(self.model).values(**data).returning(self.model.id)
                result = await session.execute(stmt)
                result = result.scalar_one()
                return result

    async def find_all(self, filter_by: dict = None) -> list[UserEntity]:
        async with db_manager.async_session_maker() as session:
            stmt = select(self.model)
            if filter_by:
                conditions = [getattr(self.model, key) == value for key, value in filter_by.items()]
                if conditions:
                    stmt = stmt.where(and_(*conditions))

            result = await session.execute(stmt)
            result = [row[0].to_entity() for row in result.all()]
            return result
