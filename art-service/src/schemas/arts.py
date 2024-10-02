from pydantic import BaseModel, Field
from datetime import datetime

from schemas.entities import BaseEntity, TagEntity


class ArtUploadSchema(BaseModel):
    user_id: int
    title: str | None
    tags: list[str]


class ArtCreateSchema(BaseModel):
    user_id: int
    title: str | None
    url: str
    blob_name: str
    url_generated_at: datetime


class ArtEntity(BaseEntity):
    id: int
    user_id: int
    blob_name: str
    url: str
    url_generated_at: datetime
    title: str | None
    likes_count: int = 0
    tags: list[TagEntity] | None = None
    created_at: datetime | None = None