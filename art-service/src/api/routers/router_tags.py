from fastapi import Depends

from api.dependencies import get_tags_service, get_user_data
from api.descriptions.tag_descrs import description_get_tags, description_post_tag, \
    description_delete_tag
from api.routers.router import router
from exceptions.http_exc import ForbiddenHTTPException
from schemas.entities import TagEntity, UserEntity
from services.tags import TagsService


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
