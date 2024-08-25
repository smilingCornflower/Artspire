from fastapi import APIRouter, Depends
from schemas.users import (
    UserCreateSchema,
    UserLoginSchema,
    UserReadSchema,
)
from config import logger
from services.users import UserService
from schemas.tokens import TokenInfoSchema
from .dependencies import get_user_service, get_current_user, get_decoded_refresh_token

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/register")
async def register_user(
        user_create_data: UserCreateSchema,
        user_service: UserService = Depends(get_user_service)
) -> int:
    new_user_id: int = await user_service.add_user(user_create_data)
    return new_user_id


@router.post("/login", response_model=TokenInfoSchema)
async def login_user(
        user_login_data: UserLoginSchema,
        user_service=Depends(get_user_service)
) -> TokenInfoSchema:
    token_data: TokenInfoSchema = await user_service.validate_user(user_login_data)
    return token_data


@router.post("/refresh")
async def refresh_jwt(
        decoded_refresh: dict = Depends(get_decoded_refresh_token),
        user_service: UserService = Depends(get_user_service)
) -> TokenInfoSchema:
    logger.debug(f"decoded_refresh: {decoded_refresh}")
    user_id: int = decoded_refresh["sub"]
    new_access_token: TokenInfoSchema = await user_service.create_token_for_user_by_id(user_id=user_id, include_refresh=False)
    return new_access_token


@router.get("/me")
async def current_user_info(
        user: UserReadSchema = Depends(get_current_user)
):
    return user
