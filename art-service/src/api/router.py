from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, UploadFile, Path, Query, status
from fastapi.security.http import HTTPBearer
from fastapi.responses import JSONResponse

from services.tags import TagsService
from schemas.arts import ArtUploadSchema
from schemas.entities import UserEntity

from .dependencies import (
    get_art_upload_data,
    get_arts_service,
    get_user_data,
    get_tags_service,
    get_users_to_saves_service,
)
from .descriptions import (
    description_get_arts, description_post_art, description_delete_art,
    description_get_tags, description_post_tag, description_delete_tag,
    description_post_user_save, description_delete_user_save
)
from exceptions.http_exc import (
    UnauthorizedHTTPException,
    FailedUploadHttpException,
    ForbiddenHTTPException,
)

from rabbit.jwt_client import run_jwt_client
from typing import Annotated

if TYPE_CHECKING:
    from fastapi.security.http import HTTPAuthorizationCredentials
    from services.arts import ArtsService
    from schemas.entities import TagEntity, ArtEntity
    from services.users_to_saves import UsersToSavesService

router = APIRouter(
    prefix="/arts",
)


@router.get("", description=description_get_arts, tags=["arts"])
async def get_arts(
        art_id: int | None = None,
        art_service: "ArtsService" = Depends(get_arts_service),
) -> list:
    one_or_all_arts: "list[ArtEntity]" = await art_service.get_arts(art_id=art_id)
    return one_or_all_arts


@router.post("", description=description_post_art, tags=["arts"], status_code=201)
async def post_art(
        art_file: UploadFile,
        art_upload_data: Annotated["ArtUploadSchema", Depends(get_art_upload_data)],
        art_service: Annotated["ArtsService", Depends(get_arts_service)],
) -> int:
    new_art_id: int = await art_service.add_art(art_data=art_upload_data, art_file=art_file)
    return new_art_id


@router.delete("", description=description_delete_art, tags=["arts"])
async def delete_art(
        art_id: int,
        user_data: "UserEntity" = Depends(get_user_data),
        art_service: "ArtsService" = Depends(get_arts_service),
) -> bool:
    art_entity: list["ArtEntity"] = await art_service.get_arts(art_id=art_id)
    art_entity: "ArtEntity" = art_entity[0]
    if art_entity.user_id == user_data.id:
        art_delete_result: bool = await art_service.delete_art(art_id=art_id)
    elif user_data.role_id == 2:  # if user is a moderator
        art_delete_result: bool = await art_service.delete_art(art_id=art_id)
    else:
        raise ForbiddenHTTPException
    return art_delete_result


@router.get("/tags", description=description_get_tags, tags=["tags"])
async def get_tags(
        tag_service: "TagsService" = Depends(get_tags_service)
) -> list:
    all_tags: list["TagEntity"] = await tag_service.get_tags()
    return all_tags


@router.post("/tags", description=description_post_tag, tags=["tags"], status_code=201)
async def post_tag(
        tag_name: str,
        user_data: "UserEntity" = Depends(get_user_data),
        tag_service: "TagsService" = Depends(get_tags_service)
) -> int:
    if user_data.role_id != 2:  # if user is not a moderator
        raise ForbiddenHTTPException
    new_tag_id: int = await tag_service.add_tag(tag_name)
    return new_tag_id


@router.delete("/tags", description=description_delete_tag, tags=["tags"])
async def delete_tag(
        tag_id: int,
        user_data: "UserEntity" = Depends(get_user_data),
        tag_service: "TagsService" = Depends(get_tags_service)
) -> bool:
    if user_data.role_id != 2:
        raise ForbiddenHTTPException
    tag_delete_result: bool = await tag_service.delete_tag(tag_id)
    return tag_delete_result


@router.post("/save", description=description_post_user_save, tags=["user_saves"], status_code=201)
async def post_user_save(
        art_id: int,
        user_data: Annotated["UserEntity", Depends(get_user_data)],
        users_to_saves_service: Annotated[
            "UsersToSavesService", Depends(get_users_to_saves_service)],
) -> bool:
    result: bool = await users_to_saves_service.save_art(user_id=user_data.id, art_id=art_id)
    return result


@router.delete("/save", description=description_delete_user_save, tags=["user_saves"])
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
