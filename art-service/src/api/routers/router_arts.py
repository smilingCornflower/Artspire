from typing import Annotated, TYPE_CHECKING

from fastapi import Body, Depends, Query

from api.dependencies import (get_art_post_schema, get_db_gateway, get_user_data,
                              get_user_data_or_none)
from api.descriptions.art_descrs import (description_delete_art, description_get_arts,
                                         description_get_similar_arts, description_post_art)
from exceptions.http_exc import ForbiddenHTTPException
from schemas.arts import ArtEntity, ArtGetResponseFull, ArtGetResponseShort, ArtPostSchema
from schemas.user import UserEntity
from .router import router

if TYPE_CHECKING:
    from services.arts import ArtsService
    from api.dependencies.get_services import DBGateway


@router.get(
    "",
    description=description_get_arts,
    tags=["arts"],
    response_model=list[ArtGetResponseFull] | list[ArtGetResponseShort]
)
async def get_arts(
        db_gateway: Annotated["DBGateway", Depends(get_db_gateway)],
        user_data: Annotated["UserEntity", Depends(get_user_data_or_none)],
        art_id: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        random_seed: Annotated[float, Query(
            ge=-1.0, le=1.0, description="Random seed must be between -1.0 and 1.0")] = None
) -> list:
    if user_data:
        user_id = user_data.id
    else:
        user_id = None
    art_service: "ArtsService" = db_gateway.get_arts_service()
    one_or_all_arts: list = await art_service.get_arts(
        art_id=art_id,
        offset=offset,
        limit=limit,
        include_likes_for_user_id=user_id,
        random_seed=random_seed,
    )
    return one_or_all_arts


@router.get(
    "/similars",
    description=description_get_similar_arts,
    tags=["arts"],
    response_model=list[ArtGetResponseShort]
)
async def get_similar_arts(
        db_gateway: Annotated["DBGateway", Depends(get_db_gateway)],
        user_data: Annotated["UserEntity", Depends(get_user_data_or_none)],
        art_id: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
) -> list:
    if user_data:
        user_id = user_data.id
    else:
        user_id = None
    art_service: "ArtsService" = db_gateway.get_arts_service()
    similar_arts: list = await art_service.get_similar_arts(
        art_id=art_id,
        offset=offset,
        limit=limit,
        include_likes_for_user_id=user_id,
    )
    return similar_arts


@router.post(
    "", description=description_post_art, tags=["arts"], response_model=int, status_code=201
)
async def post_art(
        art_post_data: Annotated["ArtPostSchema", Depends(get_art_post_schema)],
        db_gateway: Annotated["DBGateway", Depends(get_db_gateway)],
) -> int:
    art_service: "ArtsService" = db_gateway.get_arts_service()
    new_art_id: int = await art_service.add_art(art_data=art_post_data)
    return new_art_id


@router.delete(
    "", description=description_delete_art, response_model=bool, tags=["arts"]
)
async def delete_art(
        db_gateway: Annotated["DBGateway", Depends(get_db_gateway)],
        user_data: Annotated["UserEntity", Depends(get_user_data)],
        art_id: int = Body(..., embed=True),
) -> bool:
    art_service: "ArtsService" = db_gateway.get_arts_service()

    art_entity: list["ArtEntity"] = await art_service.get_arts(art_id=art_id)
    art_entity: "ArtEntity" = art_entity[0]
    if art_entity.user_id == user_data.id:
        art_delete_result: bool = await art_service.delete_art(art_id=art_id)
    elif user_data.role_id == 2:  # if user is a moderator
        art_delete_result: bool = await art_service.delete_art(art_id=art_id)
    else:
        raise ForbiddenHTTPException
    return art_delete_result
