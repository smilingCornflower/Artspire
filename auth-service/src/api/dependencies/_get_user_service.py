from services.users import UserService
from repositories.users import UserRepository
from config import settings, logger


def get_user_service() -> UserService:
    return UserService(user_repo=UserRepository())