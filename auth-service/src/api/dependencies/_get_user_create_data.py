from fastapi import Form
from pydantic import EmailStr
from typing import Annotated
from schemas.users import UserCreateSchema


async def get_user_create_data(
        username: Annotated[str, Form()],
        email: Annotated[EmailStr, Form()],
        password: Annotated[str, Form()],
) -> "UserCreateSchema":
    user_create_data: "UserCreateSchema" = UserCreateSchema(
        username=username,
        email=email,
        password=password,
    )
    return user_create_data
