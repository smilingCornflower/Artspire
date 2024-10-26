from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, Cookie, Request
from utils.jwt_utils import (
    decode_jwt,
    TOKEN_TYPE_FIELD,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE
)
from exceptions.http import (
    InvalidTokenTypeHTTPException,
    InvalidTokenHTTPException,
    UnauthorizedHTTPException,
)
from jwt.exceptions import PyJWTError, ExpiredSignatureError
from config import settings, logger
from typing import Callable


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


def _get_decoded_token(
        token_type: str,
        token: str,
) -> dict:
    try:
        decoded_token: dict = decode_jwt(token=token)
    except ExpiredSignatureError as err:
        # TODO: Finish logic for expired token
        logger.debug(f"in ExpiredSignatureError")
        raise HTTPException(status_code=401, detail="Token expired")
    except PyJWTError as err:
        logger.debug(f"in PyJWTError")
        raise InvalidTokenHTTPException
    except Exception as err:
        logger.debug(f"Unexpected exception: {err}")
        raise err

    decoded_token_type: str = decoded_token.get(TOKEN_TYPE_FIELD)
    logger.debug(f"decoded_token_type: {decoded_token_type}")

    if decoded_token_type != token_type:
        logger.debug(f"in InvalidTokenTypeHTTPException")
        raise InvalidTokenTypeHTTPException(received_type=decoded_token_type,
                                            expected_type=token_type)

    return decoded_token


def get_decoded_access_token(
        credentials: HTTPAuthorizationCredentials = Depends(custom_http_bearer)
) -> dict:
    logger.debug(f"I am here")
    return _get_decoded_token(token_type=ACCESS_TOKEN_TYPE, token=credentials.credentials)


def get_decoded_refresh_token(
        jwt_refresh: str = Cookie(None),
) -> dict:
    logger.debug(f"jwt_refresh: {jwt_refresh}")
    return _get_decoded_token(token_type=REFRESH_TOKEN_TYPE, token=jwt_refresh)
