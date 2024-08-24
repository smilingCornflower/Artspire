from fastapi import APIRouter
from fastapi.responses import JSONResponse

from database import db_manager
from models import UserOrm
from schemas import UserCreateSchema
from service import create_user_in_db
from config import settings

from exc import (
    UsernameAlreadyExistError,
    EmailAlreadyExistsHTTPError,
    WeakPasswordHTTPError,
)

from loguru import logger

logger.add(settings.logs_path,
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{file} | {function} | {line}] \n \t {message}",
           level="DEBUG",
           rotation="10 MB",
           compression="zip")


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post("/register")
async def create_new_user(
        user: UserCreateSchema
) -> JSONResponse:
    try:
        logger.debug(f"Input user: {repr(user)}")
        new_user: UserOrm = await create_user_in_db(user=user)
        logger.debug(f"new_user: {repr(new_user)}")

    except (UsernameAlreadyExistError, EmailAlreadyExistsHTTPError, WeakPasswordHTTPError) as err:
        raise err
    return JSONResponse(content=f"User created successfully")
