from repositories.repository import AbstractRepository
from config import settings
from schemas.users import (
    UserCreateSchema,
    UserLoginSchema,
    UserEntity,
)
from schemas.tokens import AccessTokenInfoSchema
from utils.password import hash_password, check_password
from utils.jwt import encode_jwt

from exceptions.http import (
    UsernameAlreadyExistHTTPException,
    EmailAlreadyExistsHTTPException,
    WeakPasswordHTTPException,
    UnauthorizedHTTPException,
    UserNotActiveHTTPException,
)

from loguru import logger

logger.add(settings.logs_path,
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{file} | {function} | {line}] \n \t {message}",
           level="DEBUG",
           rotation="10 MB",
           compression="zip")


class UserService:
    def __init__(self, user_repo: AbstractRepository):
        self.user_repo = user_repo

    def _create_access_token(self, user: UserEntity) -> AccessTokenInfoSchema:
        to_jwt_payload: dict = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "profile_image": user.profile_image,
        }
        encoded: str = encode_jwt(payload=to_jwt_payload)
        access_token: AccessTokenInfoSchema = AccessTokenInfoSchema(
            access_token=encoded,
            token_type="Bearer"
        )
        return access_token

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

    async def validate_user(self, user: UserLoginSchema) -> AccessTokenInfoSchema:
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

        token_data: AccessTokenInfoSchema = self._create_access_token(user=user_entity)

        return token_data
