from typing import TYPE_CHECKING
from fastapi import Depends, Body

from api.dependencies import get_db_gateway, get_user_data
from api.dependencies.get_services import DBGateway
from api.descriptions.tag_descrs import (
    description_get_tags,
    description_post_tag,
    description_delete_tag,
    description_search_tag,
)
from api.routers.router import router
from exceptions.http_exc import ForbiddenHTTPException
from schemas.entities import UserEntity, TagEntity
from typing import Annotated

if TYPE_CHECKING:
    from services.tags import TagsService


@router.get(
    "/tags",
    description=description_get_tags,
    tags=["tags"],
    response_model=list[TagEntity],
)
async def get_tags(
    db_gateway: Annotated["DBGateway", Depends(get_db_gateway)],
) -> list:
    tag_service: "TagsService" = db_gateway.get_tags_service()
    all_tags: list["TagEntity"] = await tag_service.get_tags()
    return all_tags


@router.post(
    "/tags",
    description=description_post_tag,
    tags=["tags"],
    response_model=int,
    status_code=201,
)
async def post_tag(
    tag_name: Annotated[str, Body(..., embed=True, min_length=2, max_length=30)],
    db_gateway: Annotated["DBGateway", Depends(get_db_gateway)],
    user_data: "UserEntity" = Depends(get_user_data),
) -> int:
    tag_service: "TagsService" = db_gateway.get_tags_service()
    if user_data.role_id != 2:  # if user is not a moderator
        raise ForbiddenHTTPException
    new_tag_id: int = await tag_service.add_tag(tag_name)
    return new_tag_id


@router.delete(
    "/tags", description=description_delete_tag, response_model=bool, tags=["tags"]
)
async def delete_tag(
    tag_id: Annotated[int, Body(..., embed=True)],
    db_gateway: Annotated["DBGateway", Depends(get_db_gateway)],
    user_data: "UserEntity" = Depends(get_user_data),
) -> bool:
    tag_service: "TagsService" = db_gateway.get_tags_service()
    if user_data.role_id != 2:
        raise ForbiddenHTTPException
    tag_delete_result: bool = await tag_service.delete_tag(tag_id)
    return tag_delete_result


@router.get(
    "/tags/search",
    tags=["tags"],
    description=description_search_tag,
    response_model=list[TagEntity],
)
async def search_tag(
    tag_part: str,
    db_gateway: Annotated["DBGateway", Depends(get_db_gateway)],
) -> list["TagEntity"]:
    tag_service: "TagsService" = db_gateway.get_tags_service()
    result_tags: list["TagEntity"] = await tag_service.tag_search(tag_part)
    return result_tags
