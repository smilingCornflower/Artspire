from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse

from models import UserOrm
from schemas import UserCreateSchema, UserReadSchema, TokenInfoSchema
from service import create_user_in_db, validate_auth_data
from config import settings

from exc import (
    UsernameAlreadyExistHTTPError,
    EmailAlreadyExistsHTTPError,
    WeakPasswordHTTPError,
    InterServerHTTPError,
    UnauthorizedHTTPError,
)
from utils import encode_jwt

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
@logger.catch(exclude=HTTPException, reraise=True)
async def create_new_user(
        user: UserCreateSchema
) -> JSONResponse:
    try:
        new_user: UserOrm = await create_user_in_db(user=user)

    except (UsernameAlreadyExistHTTPError, EmailAlreadyExistsHTTPError, WeakPasswordHTTPError) as err:
        raise err
    except ValueError as err:
        raise InterServerHTTPError

    return JSONResponse(content=f"User created successfully")


@router.post("/login", response_model=TokenInfoSchema)
@logger.catch(exclude=HTTPException, reraise=True)
async def auth_user_jwt(
        username: str = Form(),
        password: str = Form(),
) -> TokenInfoSchema:
    try:
        user_schema: UserReadSchema = await validate_auth_data(username=username, password=password)
    except UnauthorizedHTTPError as err:
        raise err

    jwt_payload: dict = {
        "sub": user_schema.id,
        "username": user_schema.username,
        "email": user_schema.email,
        "profile_image": user_schema.profile_image,
    }
    jwt_token: str = encode_jwt(payload=jwt_payload)

    token_info: TokenInfoSchema = TokenInfoSchema(
        access_token=jwt_token,
        token_type="Bearer"
    )
    return token_info


