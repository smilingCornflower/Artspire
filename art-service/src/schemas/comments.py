from schemas.entities import BaseEntity
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(extra="forbid")


class CommentOutSchema(BaseModel):
    id: int
    user_id: int
    user_username: str
    user_profile_image: str | None
    text: str
    likes_count: int
    dislikes_count: int
    is_edited: bool
    created_at: datetime

