from typing import TYPE_CHECKING
from fastapi import Depends, status, HTTPException, Request
from fastapi.security.http import HTTPBearer
from rabbit.jwt_client import run_jwt_client
from config import logger
from exceptions.http_exc import UnauthorizedHTTPException
from schemas.user import UserEntity

if TYPE_CHECKING:
    from fastapi.security.http import HTTPAuthorizationCredentials


class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request):
        try:
            credentials = await super().__call__(request)
            return credentials
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing token"
            )


custom_http_bearer = CustomHTTPBearer()
http_bearer_without_error = HTTPBearer(auto_error=False)


async def get_user_data(
        credentials: "HTTPAuthorizationCredentials" = Depends(custom_http_bearer)
) -> UserEntity:
    token: str = credentials.credentials
    jwt_response: dict = await run_jwt_client(body=token)
    if not jwt_response["is_valid"]:
        raise UnauthorizedHTTPException
    user_data: dict = jwt_response["decoded"]

    user_data: "UserEntity" = UserEntity(
        id=user_data["sub"],
        username=user_data["username"],
        email=user_data["email"],
        profile_image=user_data["profile_image"],
        role_id=user_data["role_id"],
    )
    return user_data


async def get_user_data_or_none(
        credentials: "HTTPAuthorizationCredentials" = Depends(http_bearer_without_error)
) -> UserEntity | None:
    if credentials:
        return await get_user_data(credentials=credentials)
