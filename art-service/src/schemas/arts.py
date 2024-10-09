from pydantic import BaseModel, Field, ConfigDict
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
    views_count: int = 0
    tags: list[TagEntity] | None = None
    created_at: datetime | None = None


class ArtOutShortSchema(BaseModel):
    id: int
    url: str
    is_liked: bool = False

    model_config = ConfigDict(from_attributes=True)


class ArtOutFullSchema(ArtOutShortSchema):
    id: int
    user_id: int
    url: str
    title: str | None
    likes_count: int = 0
    views_count: int = 0
    is_liked: bool = False
    tags: list[TagEntity] | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
