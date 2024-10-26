from typing import TYPE_CHECKING
from exceptions.http import FailedToSubscribeHTTPException
from config import logger
from sqlalchemy.exc import IntegrityError
from exceptions.http import UserNotExistsHTTPException

if TYPE_CHECKING:
    from repositories.subscriptions import SubscriptionsRepository
    from repositories.users import UserRepository


class SubscriptionsService:
    def __init__(self, repo: "SubscriptionsRepository", user_repo: "UserRepository"):
        self.repo = repo
        self.user_repo = user_repo

    async def add_subscription(self, follower_id: int, artist_id: int):
        """
        Adds a subscription between a follower and an artist after validating the artist's existence.

        This method ensures the artist user exists in the database before calling the repository
        to create a subscription link between a follower and an artist.

        Args:
            follower_id (int): The ID of the follower user.
            artist_id (int): The ID of the artist user.

        Returns:
            bool: True if the subscription was successfully added, False if it already exists.

        Raises:
            UserNotExistsHTTPException: If the artist user does not exist.
        """
        logger.warning(f"STARTED add_subscription()")
        user_artist: list = await self.user_repo.find_all({"id": artist_id})
        if not user_artist:
            raise UserNotExistsHTTPException(f"User with artis_id={artist_id} does not exists")

        result: bool = await self.repo.add_subscription(follower_id, artist_id)

        return result
