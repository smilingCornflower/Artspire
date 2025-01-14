from typing import Annotated, TYPE_CHECKING

from fastapi import Depends

from api.dependencies import get_db_gateway, get_user_data
from api.dependencies.get_services import DBGateway
from api.descriptions.comment_descr import (description_get_comments, description_post_comment)
from schemas.comments import CommentCreateSchema, CommentOutSchema, CommentUploadSchema
from schemas.user import UserEntity
from .router import router

if TYPE_CHECKING:
    from services.comments import CommentsService


@router.post(
    "/comments",
    tags=["comments"],
    description=description_post_comment,
    response_model=int,
    status_code=201,
)
async def post_comment(
    comment_data: CommentUploadSchema,
    db_gateway: Annotated["DBGateway", Depends(get_db_gateway)],
    user_data: "UserEntity" = Depends(get_user_data),
) -> int:
    comments_service: "CommentsService" = db_gateway.get_comments_service()
    comment_create_data = CommentCreateSchema(
        user_id=user_data.id,
        art_id=comment_data.art_id,
        text=comment_data.text,
    )
    comment_id: int = await comments_service.add_comment(
        comment_create_data=comment_create_data
    )
    return comment_id


@router.get(
    "/comments/{art_id}",
    tags=["comments"],
    description=description_get_comments,
    response_model=list[CommentOutSchema],
)
async def get_comments(
    art_id: int,
    db_gateway: Annotated["DBGateway", Depends(get_db_gateway)],
    offset: int | None = None,
    limit: int | None = None,
) -> list["CommentOutSchema"]:
    comments_service: "CommentsService" = db_gateway.get_comments_service()
    result_comments = await comments_service.get_comments(
        art_id=art_id,
        offset=offset,
        limit=limit,
    )
    return result_comments
