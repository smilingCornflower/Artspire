from fastapi import APIRouter, Form, Depends
from schemas.users import (
    UserCreateSchema,
    UserLoginSchema,
)
from schemas.tokens import AccessTokenInfoSchema
from .dependencies import get_user_service

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/register")
async def register_user(
        user_create_data: UserCreateSchema,
        user_service=Depends(get_user_service)
) -> int:
    new_user_id: int = await user_service.add_user(user_create_data)
    return new_user_id


@router.post("/login")
async def login_user(
        user_login_data: UserLoginSchema,
        user_service=Depends(get_user_service)
) -> AccessTokenInfoSchema:
    token_data: AccessTokenInfoSchema = await user_service.validate_user(user_login_data)
    return token_data
