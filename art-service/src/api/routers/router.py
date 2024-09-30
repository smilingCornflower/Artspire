from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, UploadFile, Body

from schemas.arts import ArtUploadSchema, ArtEntity
from schemas.entities import UserEntity

from api.dependencies import (
    get_art_upload_data,
    get_arts_service,
    get_user_data,
)
from api.descriptions.art_descrs import description_get_arts, description_post_art, \
    description_delete_art
from exceptions.http_exc import ForbiddenHTTPException

from typing import Annotated

if TYPE_CHECKING:
    from services.arts import ArtsService

router = APIRouter(
    prefix="/arts",
)


@router.get("", description=description_get_arts, tags=["arts"],
            response_model=list[ArtEntity])
async def get_arts(
        art_id: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        include_tags: bool = False,
        art_service: "ArtsService" = Depends(get_arts_service),
) -> list:
    one_or_all_arts: "list[ArtEntity]" = await art_service.get_arts(
        art_id=art_id,
        offset=offset,
        limit=limit,
        include_tags=include_tags,
    )
    return one_or_all_arts


@router.post("", description=description_post_art, tags=["arts"],
             response_model=int, status_code=201)
async def post_art(
        art_file: UploadFile,
        art_upload_data: Annotated["ArtUploadSchema", Depends(get_art_upload_data)],
        art_service: Annotated["ArtsService", Depends(get_arts_service)],
) -> int:
    new_art_id: int = await art_service.add_art(art_data=art_upload_data, art_file=art_file)
    return new_art_id


@router.delete("", description=description_delete_art,
               response_model=bool, tags=["arts"])
async def delete_art(
        art_id: int = Body(..., embed=True),
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
