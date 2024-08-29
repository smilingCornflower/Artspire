from typing import TYPE_CHECKING
from fastapi import Depends
from fastapi.security.http import HTTPBearer
from rabbit.jwt_client import run_jwt_client
from config import logger

if TYPE_CHECKING:
    from fastapi.security.http import HTTPAuthorizationCredentials
http_bearer = HTTPBearer()


async def get_user_data(
        credentials: "HTTPAuthorizationCredentials" = Depends(http_bearer)
) -> dict:
    token: str = credentials.credentials
    logger.debug(f"Received token: {token}")
    decoded: dict = await run_jwt_client(body=token)
    logger.info(f"Token is decoded: {decoded}")
    return decoded
