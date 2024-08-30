from typing import TYPE_CHECKING
from fastapi import Depends
from fastapi.security.http import HTTPBearer
from rabbit.jwt_client import run_jwt_client
from config import logger
from exceptions.http_exc import UnauthorizedHTTPException
from schemas.entities import UserEntity

if TYPE_CHECKING:
    from fastapi.security.http import HTTPAuthorizationCredentials
http_bearer = HTTPBearer()


async def get_user_data(
        credentials: "HTTPAuthorizationCredentials" = Depends(http_bearer)
) -> UserEntity:
    token: str = credentials.credentials
    logger.debug(f"Received token: {token}")
    decoded: dict = await run_jwt_client(body=token)
    if not decoded["is_valid"]:
        raise UnauthorizedHTTPException
    user_data: "UserEntity" = UserEntity(
        id=decoded["decoded"]["sub"],
        username=decoded["decoded"]["username"],
        email=decoded["decoded"]["email"],
        profile_image=decoded["decoded"]["profile_image"],
    )
    logger.info(f"user_data: {user_data}")
    return user_data
