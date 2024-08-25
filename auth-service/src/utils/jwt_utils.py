import jwt

import jwt_utils
from config import settings
from datetime import datetime, timedelta, timezone
from copy import deepcopy

from typing import Any

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def encode_jwt(
        payload: dict,
        private_key: str = settings.jwt_private_key_path.read_text(),
        algorithm: str = "RS256",
        expire_minutes: int = settings.jwt_access_token_expire_minutes,
) -> str:
    now: datetime = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=expire_minutes)
    to_encode: dict = deepcopy(payload)
    to_encode.update(
        iat=now,
        exp=expire,
    )

    encoded: str = jwt.encode(
        payload=to_encode,
        key=private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
        token: str,
        public_key: str = settings.jwt_public_key_path.read_text(),
        algorithm: str = "RS256",
) -> Any:
    decoded: Any = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )
    return decoded


def create_jwt(
        token_type: str,
        token_data: dict,
        expire_minutes: int = settings.jwt_access_token_expire_minutes,
) -> str:
    jwt_payload: dict = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    encoded: str = encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes
    )
    return encoded


def create_access_jwt(token_data: dict) -> str:
    access_token: str = create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=token_data,
        expire_minutes=settings.jwt_access_token_expire_minutes,
    )
    return access_token


def create_refresh_jwt(token_data: dict) -> str:
    refresh_token: str = create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=token_data,
        expire_minutes=settings.jwt_refresh_token_expire_minutes,
    )
    return refresh_token