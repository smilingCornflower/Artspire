from fastapi import Depends
from utils.jwt_utils import ACCESS_TOKEN_TYPE
from schemas.users import UserReadSchema
from config import settings, logger
from ._get_decoded_token import get_decoded_access_token


def get_current_user(
        user_data: dict = Depends(get_decoded_access_token)
) -> UserReadSchema:
    print(1)
    logger.debug(f"user_data: {user_data}")
    user: UserReadSchema = UserReadSchema(
        id=user_data["sub"],
        username=user_data["username"],
        email=user_data["email"],
        profile_image=user_data["profile_image"],
    )
    return user
