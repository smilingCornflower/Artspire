from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, UploadFile
from fastapi.security.http import HTTPBearer
from fastapi.responses import JSONResponse

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
    from schemas.entities import TagEntity, ArtEntity

router = APIRouter(
    prefix="/arts",
    tags=["Arts"],
)


@router.get("")
async def get_arts(
        art_id: int | None = None,
        art_service: "ArtsService" = Depends(get_arts_service),
) -> list:
    one_or_all_arts: "list[ArtEntity]" = await art_service.get_arts(art_id=art_id)
    return one_or_all_arts


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
    """
    Creates a new tag.

    Requires the user to be a moderator (role_id = 2).

    @param tag_name: The name of the tag to be created.
    @param user_data: The user making the request, used to check authorization.
    @param tag_service: Service for handling tag operations.
    @return: The ID of the newly created tag.
    """
    if user_data.role_id != 2:
        raise ForbiddenHTTPException
    new_tag_id: int = await tag_service.add_tag(tag_name)
    return new_tag_id


@router.get("/tags")
async def get_tags(
        tag_service: "TagsService" = Depends(get_tags_service)
) -> list:
    """
    Retrieves a list of all tags.

    Fetches and returns all tags from the tag service.

    @param tag_service: Service for tag operations.
    @return: List of tag entities. Each tag entity is a dictionary with keys 'id' (int) and 'name' (str).
    """
    all_tags: list["TagEntity"] = await tag_service.get_tags()
    return all_tags


@router.delete("/tags")
async def delete_tag(
        tag_id: int,
        user_data: "UserEntity" = Depends(get_user_data),
        tag_service: "TagsService" = Depends(get_tags_service)
) -> int:
    """
    Deletes a tag by ID.

    Checks user permissions and deletes the tag if allowed. Returns 1 if successful, 0 if not found.
    Raises Internal Server Error on failure.

    @param tag_id: id of the tag to delete.
    @param user_data: User information for permission checks.
    @param tag_service: Service for tag operations.
    @return: 1 if tag deleted, 0 if tag not found.
    @raises ForbiddenHTTPException: If the user lacks permissions.
    """
    if user_data.role_id != 2:
        raise ForbiddenHTTPException
    tag_delete_result = await tag_service.delete_tag(tag_id)
    return tag_delete_result
