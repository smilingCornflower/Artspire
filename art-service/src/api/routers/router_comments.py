from fastapi import Depends
from typing import Annotated

from .router import router
from api.dependencies import get_user_data, get_comments_service
from api.descriptions.comment_descr import (
    description_post_comment,
    description_get_comments,
)
from schemas.comments import CommentUploadSchema, CommentCreateSchema
from schemas.entities import UserEntity
from services.comments import CommentsService


@router.post("/comments", tags=["comments"], description=description_post_comment, status_code=201)
async def post_comment(
        comment_data: CommentUploadSchema,
        comments_service: Annotated["CommentsService", Depends(get_comments_service)],
        user_data: "UserEntity" = Depends(get_user_data),
) -> int:
    comment_create_data = CommentCreateSchema(
        user_id=user_data.id,
        art_id=comment_data.art_id,
        text=comment_data.text,
    )
    comment_id: int = await comments_service.add_comment(comment_create_data=comment_create_data)
    return comment_id


@router.get("/comments/{art_id}", tags=["comments"], description=description_get_comments)
async def get_comments(
        art_id: int,
        comments_service: Annotated["CommentsService", Depends(get_comments_service)],
        offset: int | None = None,
        limit: int | None = None,
) -> list:
    result_comments = await comments_service.get_comments(
        art_id=art_id,
        offset=offset,
        limit=limit,
    )
    return result_comments

