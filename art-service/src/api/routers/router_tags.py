from fastapi import Depends

from api.dependencies import get_tags_service, get_user_data
from api.descriptions.tag_descrs import description_get_tags, description_post_tag, \
    description_delete_tag
from api.routers.router import router
from exceptions.http_exc import ForbiddenHTTPException
from schemas.entities import UserEntity, TagEntity
from services.tags import TagsService
from typing import Annotated


@router.get("/tags", description=description_get_tags, tags=["tags"],
            response_model=list[TagEntity])
async def get_tags(
        tag_service: Annotated["TagsService", Depends(get_tags_service)],
) -> list:
    all_tags: list["TagEntity"] = await tag_service.get_tags()
    return all_tags


@router.post("/tags", description=description_post_tag, tags=["tags"],
             response_model=int, status_code=201)
async def post_tag(
        tag_name: str,
        tag_service: Annotated["TagsService", Depends(get_tags_service)],
        user_data: "UserEntity" = Depends(get_user_data),
) -> int:
    if user_data.role_id != 2:  # if user is not a moderator
        raise ForbiddenHTTPException
    new_tag_id: int = await tag_service.add_tag(tag_name)
    return new_tag_id


@router.delete("/tags", description=description_delete_tag,
               response_model=bool, tags=["tags"])
async def delete_tag(
        tag_id: int,
        tag_service: Annotated["TagsService", Depends(get_tags_service)],
        user_data: "UserEntity" = Depends(get_user_data),
) -> bool:
    if user_data.role_id != 2:
        raise ForbiddenHTTPException
    tag_delete_result: bool = await tag_service.delete_tag(tag_id)
    return tag_delete_result


@router.get("/tags/search", tags=["tags"],
            response_model=list[TagEntity])
async def search_tag(
        tag_part: str,
        tag_service: Annotated["TagsService", Depends(get_tags_service)],
) -> list["TagEntity"]:
    result_tags: list["TagEntity"] = await tag_service.tag_search(tag_part)
    return result_tags
