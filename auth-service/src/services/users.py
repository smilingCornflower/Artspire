from repositories.repository import AbstractRepository
from config import settings, logger
from schemas.users import (
    UserCreateSchema,
    UserLoginSchema,
    UserEntity,
    UserReadSchema,
)
from schemas.tokens import TokenInfoSchema
from utils.password import hash_password, check_password
from utils.jwt_utils import create_access_jwt, create_refresh_jwt
from sqlalchemy.exc import SQLAlchemyError
from exceptions.http import (
    UsernameAlreadyExistHTTPException,
    EmailAlreadyExistsHTTPException,
    WeakPasswordHTTPException,
    UnauthorizedHTTPException,
    UserNotActiveHTTPException,
)


def create_token_for_user(user: UserEntity, include_refresh: bool = True) -> TokenInfoSchema:
    access_payload: dict = {
        "sub": user.id,
        "username": user.username,
        "email": user.email,
        "profile_image": user.profile_image,
        "role_id": user.role_id,
    }
    refresh_payload: dict = {
        "sub": user.id,
    }

    access_token: str = create_access_jwt(token_data=access_payload)
    refresh_token: str = create_refresh_jwt(token_data=refresh_payload)

    if include_refresh:
        token_info: TokenInfoSchema = TokenInfoSchema(access_token=access_token,
                                                      refresh_token=refresh_token)
    else:
        token_info: TokenInfoSchema = TokenInfoSchema(access_token=access_token)
    return token_info


class UserService:
    def __init__(self, user_repo: AbstractRepository):
        self.user_repo = user_repo

    async def add_user(self, user_create_data: UserCreateSchema) -> int:
        user_by_username: list[UserEntity] = await self.user_repo.find_all(
            filter_by={"username": user_create_data.username})

        if user_by_username:
            logger.warning(f"Username '{user_create_data.username}' already exists.")
            raise UsernameAlreadyExistHTTPException

        user_by_email = await self.user_repo.find_all(filter_by={"email": user_create_data.email})
        if user_by_email:
            logger.warning(f"Email '{user_create_data.email}' already exists.")
            raise EmailAlreadyExistsHTTPException

        if len(user_create_data.password) < 6:
            logger.warning("Provided password is too weak.")
            raise WeakPasswordHTTPException

        hashed_password = hash_password(password=user_create_data.password)
        new_user_data: dict = {
            "username": user_create_data.username,
            "email": user_create_data.email,
            "hashed_password": hashed_password,
        }
        new_user_id: int = await self.user_repo.add_one(data=new_user_data)
        logger.info(f"User '{user_create_data.username}' added with ID: {new_user_id}")
        return new_user_id

    async def validate_user(self, user: UserLoginSchema) -> TokenInfoSchema:
        user_by_username: list[UserEntity] = await self.user_repo.find_all({"username": user.username})

        if not user_by_username:
            logger.warning(f"Unauthorized access attempt for username: '{user.username}'")
            raise UnauthorizedHTTPException

        if not user_by_username[0].is_active:
            logger.warning(f"User '{user.username}' is not active.")
            raise UserNotActiveHTTPException

        user_entity: UserEntity = user_by_username[0]
        correct_password: str = user_entity.hashed_password
        check_password_result: bool = check_password(user.password, correct_password)

        if not check_password_result:
            logger.warning(f"Incorrect password attempt for user: '{user.username}'")
            raise UnauthorizedHTTPException

        token_data: TokenInfoSchema = create_token_for_user(user=user_entity)
        logger.info(f"Token created for user '{user.username}'")
        return token_data

    async def create_token_for_user_by_id(self, user_id: int, include_refresh: bool = False) -> TokenInfoSchema:
        user_by_id: list[UserEntity] = await self.user_repo.find_all({"id": user_id})
        result_token = create_token_for_user(
            user=user_by_id[0],
            include_refresh=include_refresh)
        logger.info(f"Token created for user ID: {user_id}")
        return result_token

    async def get_all_users(self, users_id: list[int]):
        result_users: list[UserEntity] = await self.user_repo.find_all({"id": users_id})
        users_info: list[dict] = []
        for user in result_users:
            user_info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "profile_image": user.profile_image,
            }
            users_info.append(user_info)
        logger.info(f"Retrieved information for {len(users_info)} users.")
        return users_info
