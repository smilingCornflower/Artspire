from fastapi import APIRouter, Depends, status, Response, Body
from schemas.users import (
    UserCreateSchema,
    UserLoginSchema,
    UserReadSchema,
)
from services.users import UserService
from services.subscriptions import SubscriptionsService
from config import logger, settings
from utils.set_httponly import set_refresh_in_httponly
from services.users import UserService
from schemas.users import UserProfilePrivate, UserProfilePublic
from schemas.tokens import TokenInfoSchema, AccessTokenSchema
from .dependencies import (
    get_user_service,
    get_current_user,
    get_current_user_or_none,
    get_decoded_refresh_token,
    get_user_create_data,
    get_user_login_data,
    get_subscription_service,

)
from .descriptions import (
    description_register,
    description_login,
    description_refresh,
    description_me,
    description_profile,
    description_post_subscribe,
    description_post_unsubscribe,
)
from typing import Annotated

router = APIRouter(
    prefix="/users",
)


class APIStatuses:
    private_profile_status_code: int = 227
    public_profile_status_code: int = 228


statuses = APIStatuses()


@router.post("/register", tags=["users"],
             response_model=int, description=description_register,
             status_code=status.HTTP_201_CREATED)
async def register_user(
        user_create_data: Annotated[UserCreateSchema, Depends(get_user_create_data)],
        user_service: UserService = Depends(get_user_service)
) -> int:
    new_user_id: int = await user_service.add_user(user_create_data)
    return new_user_id


@router.post("/login", tags=["users"],
             response_model=AccessTokenSchema, description=description_login)
async def login_user(
        response: Response,
        user_login_data: Annotated[UserLoginSchema, Depends(get_user_login_data)],
        user_service=Depends(get_user_service)
) -> AccessTokenSchema:
    token_data: AccessTokenSchema = await user_service.validate_user(response, user_login_data)

    return token_data


@router.post("/refresh", tags=["users"],
             description=description_refresh, response_model=AccessTokenSchema,
             status_code=status.HTTP_201_CREATED)
async def refresh_jwt(
        decoded_refresh: Annotated[dict, Depends(get_decoded_refresh_token)],
        user_service: Annotated[UserService, Depends(get_user_service)]
) -> AccessTokenSchema:
    logger.debug(f"decoded_refresh: {decoded_refresh}")
    user_id: int = decoded_refresh["sub"]
    new_access_token: TokenInfoSchema = await user_service.create_token_for_user_by_id(
        user_id=user_id,
    )
    access_token: AccessTokenSchema = AccessTokenSchema.model_validate(new_access_token)
    return access_token


@router.get("/me", tags=["users"],
            description=description_me, response_model=UserReadSchema)
async def current_user_info(
        user: Annotated[UserReadSchema, Depends(get_current_user)]
) -> UserReadSchema:
    return user


@router.get("/profile", tags=["users"], description=description_profile,
            response_model=UserProfilePublic | UserProfilePrivate,
            status_code=statuses.public_profile_status_code | statuses.private_profile_status_code
            )
async def get_profile_by_username(
        user: Annotated[UserReadSchema, Depends(get_current_user_or_none)],
        username: str,
        user_service: Annotated[UserService, Depends(get_user_service)],
        response: Response,
):
    if user is not None and user.username == username:
        profile_info = await user_service.get_profile_by_username(username=username, private=True)
        response.status_code = statuses.private_profile_status_code
    else:
        profile_info = await user_service.get_profile_by_username(username=username)
        response.status_code = statuses.public_profile_status_code

    return profile_info


@router.post("/subscribe", tags=["subscription"],
             description=description_post_subscribe, response_model=bool, status_code=200)
async def subscribe_to_artist(
        user: Annotated[UserReadSchema, Depends(get_current_user)],
        subscription_service: Annotated[SubscriptionsService, Depends(get_subscription_service)],
        artist_id: Annotated[int, Body(embed=True)],
) -> bool:
    result: bool = await subscription_service.add_subscription(user.id, artist_id)
    return result


@router.post("/unsubscribe", tags=["subscription"],
             description=description_post_unsubscribe, response_model=bool, status_code=200)
async def unsubscribe_from_artist(
        user: Annotated[UserReadSchema, Depends(get_current_user)],
        subscription_service: Annotated[SubscriptionsService, Depends(get_subscription_service)],
        artist_id: Annotated[int, Body(embed=True)],
) -> bool:
    result: bool = await subscription_service.remove_subscription(user.id, artist_id)
    return result
