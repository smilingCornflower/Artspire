from sqlalchemy import select

from schemas import UserCreateSchema, UserReadSchema
from models import UserOrm
from database import db_manager
from config import settings
from exc import (
    UsernameAlreadyExistHTTPError,
    EmailAlreadyExistsHTTPError,
    WeakPasswordHTTPError,
    UnauthorizedHTTPError,
    UserNotFoundSQLError
)
from utils import hash_password, check_password

from loguru import logger

# Annotations
from sqlalchemy import (
    Select,
    ChunkedIteratorResult
)
from sqlalchemy.orm import InstrumentedAttribute

logger.add(settings.logs_path,
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{file} | {function} | {line}] \n \t {message}",
           level="DEBUG",
           rotation="10 MB",
           compression="zip")


async def check_user_with_field_exists(field_name: str, value: str) -> bool:
    async with db_manager.session_factory() as session:
        column: InstrumentedAttribute = getattr(UserOrm, field_name)
        if column is None:
            raise ValueError(f"Invalid field name: {field_name}")
        stmt: Select = select(UserOrm).where(column == value)
        result: ChunkedIteratorResult = await session.execute(stmt)
        result_user: UserOrm = result.scalars().first()
        return bool(result_user)


async def get_user_by_username(username: str) -> UserOrm:
    async with db_manager.session_factory() as session:
        stmt: Select = select(UserOrm).where(UserOrm.username == username)
        result: ChunkedIteratorResult = await session.execute(stmt)

        result_user: UserOrm = result.scalars().first()
        if not result_user:
            raise UserNotFoundSQLError
        return result_user


async def create_user_in_db(user: UserCreateSchema) -> UserOrm:
    async with db_manager.session_factory() as session:
        async with session.begin():
            username_exists: bool = await check_user_with_field_exists(field_name="username",
                                                                       value=user.username)
            email_exists: bool = await check_user_with_field_exists(field_name="email",
                                                                    value=user.email)
            if username_exists:
                raise UsernameAlreadyExistHTTPError
            elif email_exists:
                raise EmailAlreadyExistsHTTPError

            if len(user.password) < 6:
                raise WeakPasswordHTTPError(detail="Password must be at least 6 characters long.")

            hashed_password = hash_password(password=user.password)

            new_user = UserOrm(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password,
                role_id=1
            )
            session.add(new_user)
            return new_user


async def validate_auth_data(username: str, password: str) -> UserReadSchema:
    async with db_manager.session_factory() as session:
        try:
            user: UserOrm = await get_user_by_username(username=username)
        except UserNotFoundSQLError as err:
            raise UnauthorizedHTTPError

        correct_hashed_password: str = user.hashed_password
        is_correct_password: bool = check_password(
            password=password,
            hashed_password=correct_hashed_password
        )
        if not is_correct_password:
            raise UnauthorizedHTTPError

        user_schema: UserReadSchema = UserReadSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            profile_image=user.profile_image,
        )
        return user_schema
