from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, UploadFile
from fastapi.security.http import HTTPBearer

from services.tags import TagsService
from schemas.arts import ArtUploadSchema
from schemas.entities import UserEntity

from .dependencies.get_user_data import get_user_data
from .dependencies.get_arts_service import get_arts_service
from .dependencies.get_tags_service import get_tags_service

from exceptions.http_exc import (
    UnauthorizedHTTPException,
    FailedUploadHttpException,
    ForbiddenHTTPException,
)

from rabbit.jwt_client import run_jwt_client

if TYPE_CHECKING:
    from fastapi.security.http import HTTPAuthorizationCredentials
    from services.arts import ArtsService
    from schemas.entities import TagEntity

router = APIRouter(
    prefix="/arts",
    tags=["Arts"],
)


@router.post("")
async def post_art(
        art_file: UploadFile,
        art_tags: str,
        art_title: str | None,
        art_service: "ArtsService" = Depends(get_arts_service),
        user_data: "UserEntity" = Depends(get_user_data),
) -> int:
    art_upload_data: "ArtUploadSchema" = ArtUploadSchema(
        user_id=user_data.id,
        title=art_title,
        tags=art_tags.split(","),
    )
    try:
        new_art_id: int = await art_service.add_art(art_data=art_upload_data, art_file=art_file)
    except FailedUploadHttpException as err:
        raise
    return new_art_id


@router.post("/tags")
async def post_tag(
        tag_name: str,
        user_data: "UserEntity" = Depends(get_user_data),
        tag_service: "TagsService" = Depends(get_tags_service)
) -> int:
    if user_data.role_id != 2:
        raise ForbiddenHTTPException
    new_tag_id: int = await tag_service.add_tag(tag_name)
    return new_tag_id


@router.get("/tags")
async def get_tags(
        tag_service: "TagsService" = Depends(get_tags_service)
) -> list:
    all_tags: list["TagEntity"] = await tag_service.get_tags()
    return all_tags
