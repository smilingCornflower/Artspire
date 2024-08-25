from repositories.repository import AbstractRepository
from config import settings, logger
from schemas.users import (
    UserCreateSchema,
    UserLoginSchema,
    UserEntity,
)
from schemas.tokens import TokenInfoSchema
from utils.password import hash_password, check_password
from utils.jwt_utils import create_access_jwt, create_refresh_jwt

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
        "profile_image": user.profile_image
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
            raise UsernameAlreadyExistHTTPException

        user_by_email = await self.user_repo.find_all(filter_by={"email": user_create_data.email})
        if user_by_email:
            raise EmailAlreadyExistsHTTPException

        if len(user_create_data.password) < 6:
            raise WeakPasswordHTTPException

        hashed_password = hash_password(password=user_create_data.password)

        new_user_data: dict = {
            "username": user_create_data.username,
            "email": user_create_data.email,
            "hashed_password": hashed_password,
        }
        new_user_id: int = await self.user_repo.add_one(data=new_user_data)

        return new_user_id

    async def validate_user(self, user: UserLoginSchema) -> TokenInfoSchema:
        user_by_username: list[UserEntity] = await self.user_repo.find_all({"username": user.username})

        if not user_by_username:
            raise UnauthorizedHTTPException

        if not user_by_username[0].is_active:
            raise UserNotActiveHTTPException

        user_entity: UserEntity = user_by_username[0]
        correct_password: str = user_entity.hashed_password
        check_password_result: bool = check_password(user.password, correct_password)

        if not check_password_result:
            raise UnauthorizedHTTPException

        token_data: TokenInfoSchema = create_token_for_user(user=user_entity)

        return token_data

    # TODO: Make one function for token creation
    async def create_token_for_user_by_id(self, user_id: int, include_refresh: bool) -> TokenInfoSchema:
        user_by_id: list[UserEntity] = await self.user_repo.find_all({"id": user_id})
        result_token = create_token_for_user(
            user=user_by_id[0],
            include_refresh=include_refresh)
        return result_token
