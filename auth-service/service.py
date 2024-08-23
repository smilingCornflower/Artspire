from sqlalchemy import select

from schemas import UserCreateSchema
from models import UserOrm
from database import db_manager
from config import settings
from exc import UsernameAlreadyExistError, EamilAlreadyExistsError
from utils import hash_password

from loguru import logger

# Annotations
from sqlalchemy import Select

logger.add(settings.logs_path,
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{file} | {function} | {line}] \n \t {message}",
           level="DEBUG",
           rotation="10 MB",
           compression="zip")


async def check_user_with_field_exists(field_name: str, value: str) -> bool:
    async with db_manager.session_factory() as session:
        column = getattr(UserOrm, field_name)
        if column is None:
            raise ValueError(f"Invalid field name: {field_name}")
        stmt = select(UserOrm).where(column == value)
        result = await session.execute(stmt)
        result_user = result.scalars().first()
        return bool(result_user)


async def create_user_in_db(user):
    async with db_manager.session_factory() as session:
        async with session.begin():
            username_exists: bool = await check_user_with_field_exists(field_name="username",
                                                                       value=user.username)
            email_exists: bool = await check_user_with_field_exists(field_name="email",
                                                                    value=user.email)
            if username_exists:
                raise UsernameAlreadyExistError
            elif email_exists:
                raise EamilAlreadyExistsError

            logger.debug(f"result_user: {result_user}")
            logger.debug(f"user: {user}")

            hashed_password = hash_password(password=user.password)

            new_user = UserOrm(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password,
                role_id=1
            )
            logger.debug(f"new_user: {new_user}")
            session.add(new_user)
            return new_user
