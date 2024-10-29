from fastapi import Depends
from utils.jwt_utils import ACCESS_TOKEN_TYPE
from schemas.users import UserReadSchema
from config import settings, logger
from ._get_decoded_token import get_decoded_access_token, get_decoded_access_token_or_none


def get_current_user(
        user_data: dict = Depends(get_decoded_access_token)
) -> UserReadSchema:
    user: UserReadSchema = UserReadSchema(
        id=user_data["sub"],
        username=user_data["username"],
        email=user_data["email"],
        profile_image=user_data["profile_image"],
    )
    return user


def get_current_user_or_none(
        user_data: dict | None = Depends(get_decoded_access_token_or_none)
) -> UserReadSchema | None:
    if user_data is None:
        return None
    return get_current_user(user_data=user_data)

