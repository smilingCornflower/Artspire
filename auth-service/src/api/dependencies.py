from services.users import UserService
from repositories.users import UserRepository


def get_user_service() -> UserService:
    return UserService(user_repo=UserRepository())