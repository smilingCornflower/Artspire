from repositories.repository import SQLAlchemyRepository
from models.users import UserOrm
from database.db import db_manager
from sqlalchemy import update, Update


class UserRepository(SQLAlchemyRepository):
    model = UserOrm

    async def change_counter(self, user_id: int, number: int, counter_name: str):
        # noinspection PyTypeChecker
        stmt: "Update" = update(self.model).where(self.model.id == user_id)
        if counter_name == "followers_count":
            stmt: "Update" = stmt.values(followers_count=self.model.followers_count + number)
        elif counter_name == "followings_count":
            stmt: "Update" = stmt.values(followings_count=self.model.followings_count + number)
        else:
            raise ValueError(f"Invalid counter name: {counter_name}")
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                result: "Result" = await session.execute(stmt)
        return result.rowcount
