from fastapi import Form
from schemas.users import UserLoginSchema
from typing import Annotated


async def get_user_login_data(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
) -> "UserLoginSchema":
    user_login_data: "UserLoginSchema" = UserLoginSchema(
        username=username,
        password=password
    )
    return user_login_data
