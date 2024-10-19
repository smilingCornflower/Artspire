from fastapi import UploadFile
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from schemas.entities import BaseEntity, TagEntity
from .base import CustomBaseModel


class ArtEntity(CustomBaseModel):
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


class ArtPostSchema(CustomBaseModel):
    user_id: int
    art_file: UploadFile
    title: str | None
    tags: list[str]


class ArtCreateDTO(CustomBaseModel):
    user_id: int
    title: str | None
    url: str
    blob_name: str
    url_generated_at: datetime


class ArtGetResponseShort(CustomBaseModel):
    id: int
    url: str
    is_liked: bool = False


class ArtGetResponseFull(CustomBaseModel):
    id: int
    user_id: int
    username: str
    url: str

    profile_image: str | None
    title: str | None
    likes_count: int
    views_count: int
    is_liked: bool = False
    tags: list[TagEntity]
    created_at: datetime
