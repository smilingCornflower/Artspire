from repositories.subscriptions import SubscriptionsRepository
from repositories.users import UserRepository
from services.subscriptions import SubscriptionsService


def get_subscription_service() -> SubscriptionsService:
    return SubscriptionsService(repo=SubscriptionsRepository(),
                                user_repo=UserRepository())
