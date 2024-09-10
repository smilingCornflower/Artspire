from typing import TYPE_CHECKING
from .repository import SQLAlchemyRepository
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models.users_to_likes import UsersToLikesOrm
from database.db import db_manager

from config import logger

if TYPE_CHECKING:
    from sqlalchemy.dialects.postgresql import Insert
    from sqlalchemy import ChunkedIteratorResult


class UsersToLikesRepository(SQLAlchemyRepository):
    model = UsersToLikesOrm

    async def add_one(self, data: dict) -> int:
        logger.debug(f"Insert data: {data}")

        async with db_manager.async_session_maker() as session:
            async with session.begin():
                try:
                    stmt: "Insert" = insert(self.model).values(**data)
                    stmt: "Insert" = stmt.on_conflict_do_nothing(
                        index_elements=["user_id", "art_id"]
                    )
                    result: "ChunkedIteratorResult" = await session.execute(stmt)
                    return result.rowcount

                except IntegrityError as err:
                    logger.error(f"IntegrityError: {err}")
                    raise err
                except SQLAlchemyError as err:
                    logger.error(f"SQLAlchemyError: {err}")
                    raise err
