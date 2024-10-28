from repositories.users import UserRepository
from config import settings, logger
from fastapi import Response
from schemas.users import (
    UserCreateSchema,
    UserLoginSchema,
    UserEntity,
    UserReadSchema,
    UserProfilePrivate,
    UserProfilePublic
)
from schemas.tokens import TokenInfoSchema, AccessTokenSchema
from utils.password import hash_password, check_password
from utils.jwt_utils import create_access_jwt, create_refresh_jwt
from utils.set_httponly import set_refresh_in_httponly
from sqlalchemy.exc import SQLAlchemyError
from exceptions.http import (
    UsernameAlreadyExistHTTPException,
    EmailAlreadyExistsHTTPException,
    WeakPasswordHTTPException,
    UnauthorizedHTTPException,
    UserNotActiveHTTPException,
    UserNotFoundHTTPException,
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
    def __init__(self, user_repo: UserRepository):
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

    async def validate_user(self, response: Response, user: UserLoginSchema) -> AccessTokenSchema:

        user_by_username: list[UserEntity] = await self.user_repo.find_all(
            {"username": user.username})

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

        set_refresh_in_httponly(response=response, refresh_token=token_data.refresh_token)
        access_toke_data: AccessTokenSchema = AccessTokenSchema.model_validate(token_data)

        logger.info(f"Token created for user '{user.username}'")
        return access_toke_data

    async def create_token_for_user_by_id(self, user_id: int,
                                          include_refresh: bool = False) -> TokenInfoSchema:
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

    import logging

    logger = logging.getLogger(__name__)

    async def get_profile_by_username(
            self, username: str, private: bool = False
    ) -> "UserProfilePrivate | UserProfilePublic":
        logger.info(f"Retrieving profile for username: {username}, private view: {private}")

        result_users: list[UserEntity] = await self.user_repo.find_all({"username": username})

        if not result_users:
            logger.warning(f"User '{username}' not found")
            raise UserNotFoundHTTPException(detail="User with such username not found")

        user = result_users[0]
        logger.info(f"User '{username}' found")
        if private:
            user_profile = UserProfilePrivate.model_validate(user)
        else:
            user_profile = UserProfilePublic.model_validate(user)

        logger.debug(f"Profile data for user '{username}': {user_profile}")

        return user_profile
