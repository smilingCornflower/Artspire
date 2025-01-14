from typing import Annotated

from fastapi import APIRouter, Body, Depends, Response, status, UploadFile

from config import logger
from schemas.tokens import AccessTokenSchema, TokenInfoSchema
from schemas.users import UserCreateSchema, UserLoginSchema, UserProfilePrivate, UserProfilePublic, \
    UserReadSchema
from services.subscriptions import SubscriptionsService
from services.users import UserService
from .dependencies import (get_current_user, get_current_user_or_none, get_decoded_refresh_token,
                           get_subscription_service, get_user_create_data, get_user_login_data,
                           get_user_service)
from .descriptions import (
    description_change_username, description_get_profile_picture,
    description_login, description_me, description_post_profile_picture,
    description_post_subscribe, description_post_unsubscribe,
    description_profile, description_refresh, description_register)

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


@router.put("/change-username", tags=["users"], description=description_change_username,
            response_model=AccessTokenSchema, status_code=200)
async def change_username(
        user: Annotated[UserReadSchema, Depends(get_current_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        new_username: str,
) -> AccessTokenSchema:
    await user_service.change_username(user_id=user.id, new_username=new_username)
    new_access_token: TokenInfoSchema = await user_service.create_token_for_user_by_id(
        user_id=user.id,
    )
    access_token: AccessTokenSchema = AccessTokenSchema.model_validate(new_access_token)
    return access_token


@router.post("/profile-picture", tags=["users"], description=description_post_profile_picture,
             status_code=201)
async def set_profile_picture(
        user: Annotated[UserReadSchema, Depends(get_current_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        profile_picture: UploadFile,
) -> None:
    user_id: int = user.id
    await user_service.set_profile_picture(user_id=user_id, image=profile_picture)


@router.get("/profile-picture", tags=["users"], description=description_get_profile_picture,
            status_code=200)
async def get_profile_picture(
        user_id: int,
        user_service: Annotated[UserService, Depends(get_user_service)],

) -> str:
    profile_picture_url: str = await user_service.get_profile_picture(user_id=user_id)
    return profile_picture_url
