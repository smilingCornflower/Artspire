from fastapi import APIRouter, Depends, status, Response
from schemas.users import (
    UserCreateSchema,
    UserLoginSchema,
    UserReadSchema,
)
from config import logger
from utils.set_httponly import set_refresh_in_httponly
from services.users import UserService
from schemas.tokens import TokenInfoSchema, AccessTokenSchema
from .dependencies import (
    get_user_service,
    get_current_user,
    get_decoded_refresh_token,
    get_user_create_data,
    get_user_login_data,
)
from .descriptions import (
    description_register,
    description_login,
    description_refresh,
    description_me,
)
from typing import Annotated

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/register", response_model=int, description=description_register,
             status_code=status.HTTP_201_CREATED)
async def register_user(
        user_create_data: Annotated[UserCreateSchema, Depends(get_user_create_data)],
        user_service: UserService = Depends(get_user_service)
) -> int:
    new_user_id: int = await user_service.add_user(user_create_data)
    return new_user_id


@router.post("/login", response_model=AccessTokenSchema, description=description_login)
async def login_user(
        response: Response,
        user_login_data: Annotated[UserLoginSchema, Depends(get_user_login_data)],
        user_service=Depends(get_user_service)
) -> AccessTokenSchema:
    token_data: AccessTokenSchema = await user_service.validate_user(response, user_login_data)

    return token_data


@router.post("/refresh", description=description_refresh, response_model=AccessTokenSchema,
             status_code=status.HTTP_201_CREATED)
async def refresh_jwt(
        decoded_refresh: Annotated[dict, Depends(get_decoded_refresh_token)],
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> AccessTokenSchema:
    logger.debug(f"decoded_refresh: {decoded_refresh}")
    user_id: int = decoded_refresh["sub"]
    new_access_token: TokenInfoSchema = await user_service.create_token_for_user_by_id(
        user_id=user_id,
    )
    access_token: AccessTokenSchema = AccessTokenSchema.model_validate(new_access_token)
    return access_token


@router.get("/me", description=description_me, response_model=UserReadSchema)
async def current_user_info(
        user: Annotated[UserReadSchema, Depends(get_current_user)]
) -> UserReadSchema:
    return user
