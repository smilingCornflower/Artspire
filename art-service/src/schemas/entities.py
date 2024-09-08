from datetime import datetime

from pydantic import BaseModel, EmailStr


class BaseEntity(BaseModel):
    id: int


class UserEntity(BaseEntity):
    username: str
    email: EmailStr
    profile_image: str | None
    role_id: int = 1


class TagEntity(BaseEntity):
    name: str


class ArtEntity(BaseEntity):
    user_id: int
    blob_name: str
    url: str
    url_generated_at: datetime
    title: str | None = None
    likes_count: int = 0
    tags: list | dict | None = None
    created_at: datetime | None = None


class UserSavedArtsEntity(BaseEntity):
    arts: list[int]
