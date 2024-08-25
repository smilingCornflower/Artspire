import jwt
from config import settings
from datetime import datetime, timedelta, timezone
from copy import deepcopy

from typing import Any


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
