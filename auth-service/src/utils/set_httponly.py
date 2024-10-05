from fastapi import Response
from config import settings


def set_refresh_in_httponly(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="jwt_refresh",
        value=refresh_token,
        httponly=True,
        max_age=settings.jwt_refresh_token_expire_minutes * 60,
        samesite="lax",
        secure=False,
    )
