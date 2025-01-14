from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import insert as p_insert

from config import logger
from database.db import db_manager
from models.subscriptions import SubscriptionOrm
from .repository import SQLAlchemyRepository

if TYPE_CHECKING:
    from sqlalchemy.dialects.postgresql import Insert as PInsert
    from sqlalchemy.engine import Result


class SubscriptionsRepository(SQLAlchemyRepository):
    model = SubscriptionOrm

    async def add_subscription(self, follower_id: int, arist_id: int) -> bool:
        """
        Adds a subscription between a follower and an artist.

        This method attempts to create a subscription link between a follower and an artist.
        If the subscription already exists, the insert operation will be skipped.

        Args:
            follower_id (int): The ID of the follower user.
            artist_id (int): The ID of the artist user.

        Returns:
            bool: True if the subscription was successfully added, False if the subscription already exists.
        """
        async with db_manager.async_session_maker() as session:
            async with session.begin():
                to_insert: dict = {"follower_id": follower_id, "artist_id": arist_id}
                logger.debug(f"Attempting to insert subscription with data: {to_insert}")

                stmt: "PInsert" = p_insert(self.model).values(to_insert).on_conflict_do_nothing()
                result: "Result" = await session.execute(stmt)

                if result.rowcount == 0:
                    logger.info("Subscription already exists, skipping insert.")
                    return False
                else:
                    logger.info("Successfully added subscription")
                    return True
