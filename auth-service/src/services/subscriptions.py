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

    async def add_subscription(self, follower_id: int, artist_id: int) -> bool:
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
        logger.warning(f"STARTED add_subscription({follower_id}, {artist_id})")
        user_artist: list = await self.user_repo.find_all({"id": artist_id})
        if not user_artist:
            raise UserNotExistsHTTPException(f"User with artis_id={artist_id} does not exists")

        result_subscription: bool = await self.repo.add_subscription(follower_id, artist_id)

        if result_subscription:
            result_1: int = await self.user_repo.change_counter(
                user_id=artist_id, counter_name="followers_count", number=1)
            result_2: int = await self.user_repo.change_counter(
                user_id=follower_id, counter_name="followings_count", number=1)
            assert result_1 == result_2 == 1
        return result_subscription

    async def remove_subscription(self, follower_id: int, artist_id: int) -> bool:
        logger.warning(f"STARTED remove_subscription({follower_id}, {artist_id})")
        result: bool = await self.repo.delete_one(
            {"follower_id": follower_id, "artist_id": artist_id})
        if result:
            result_1: int = await self.user_repo.change_counter(
                user_id=artist_id, counter_name="followers_count", number=-1)
            result_2: int = await self.user_repo.change_counter(
                user_id=follower_id, counter_name="followings_count", number=-1)
            assert result_1 == result_2 == 1
        return result
