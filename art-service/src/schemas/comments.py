from schemas.entities import BaseEntity
from pydantic import BaseModel
from datetime import datetime


class CommentEntity(BaseEntity):
    id: int
    user_id: int
    art_id: int
    text: str
    likes_count: int
    dislikes_count: int
    is_edited: bool
    created_at: datetime


class CommentUploadSchema(BaseModel):
    art_id: int
    text: str


class CommentCreateSchema(CommentUploadSchema):
    user_id: int

    class Config:
        extra = "forbid"
