from typing import Annotated

from fastapi import Depends

from api.dependencies import get_user_data, get_users_to_saves_service, get_users_to_likes_servcie
from api.descriptions.user_like_descrs import (
    description_post_user_like,
    description_delete_user_like,
)
from api.routers.router import router
from schemas.entities import UserEntity
from schemas.arts import ArtEntity
from services.users_to_likes import UsersToLikesService
from services.users_to_saves import UsersToSavesService


@router.post("/save", description=description_post_user_like, tags=["user_saves"],
             response_model=bool, status_code=201)
async def post_user_save(
        art_id: int,
        user_data: Annotated["UserEntity", Depends(get_user_data)],
        users_saves_service: Annotated["UsersToSavesService", Depends(get_users_to_saves_service)],
) -> bool:
    result: bool = await users_saves_service.save_art(user_id=user_data.id, art_id=art_id)
    return result


@router.get("/save", tags=["user_saves"], response_model=list[ArtEntity])
async def get_user_saves(
        user_data: Annotated["UserEntity", Depends(get_user_data)],
        users_saves_service: Annotated["UsersToSavesService", Depends(get_users_to_saves_service)],
        offset: int | None = None,
        limit: int | None = None,
        include_tags: bool = False,
) -> list["ArtEntity"]:
    user_id: int = user_data.id
    result_saves: list = await users_saves_service.get_saved_arts(
        user_id=user_id,
        offset=offset,
        limit=limit,
        include_tags=include_tags,
    )
    return result_saves


@router.delete("/save", description=description_delete_user_like,
               response_model=bool, tags=["user_saves"])
async def delete_user_save(
        art_id: int,
        user_data: Annotated["UserEntity", Depends(get_user_data)],
        users_to_saves_service: Annotated[
            "UsersToSavesService", Depends(get_users_to_saves_service)],
) -> bool:
    result: bool = await users_to_saves_service.delete_from_saved(
        user_id=user_data.id,
        art_id=art_id
    )
    return result


@router.post("/like", tags=["user_likes"], response_model=bool, status_code=201)
async def post_user_like(
        art_id: int,
        user_data: Annotated["UserEntity", Depends(get_user_data)],
        user_to_likes_servcie: Annotated[
            "UsersToLikesService", Depends(get_users_to_likes_servcie)
        ],
) -> bool:
    result: bool = await user_to_likes_servcie.like_art(user_id=user_data.id, art_id=art_id)
    return result


@router.delete("/like", tags=["user_likes"], response_model=bool)
async def delete_user_like(
        art_id: int,
        user_data: Annotated["UserEntity", Depends(get_user_data)],
        users_to_saves_service: Annotated[
            "UsersToLikesService", Depends(get_users_to_likes_servcie)
        ],
) -> bool:
    result: bool = await users_to_saves_service.delete_from_liked(
        user_id=user_data.id,
        art_id=art_id
    )
    return result
