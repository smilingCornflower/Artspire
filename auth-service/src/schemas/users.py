from __future__ import annotations

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserReadSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    profile_image: str | None


class UserEntity(BaseModel):
    id: int
    username: str
    hashed_password: str
    email: EmailStr
    profile_image: str | None

    role_id: int
    is_active: bool
    followers_count: int
    followings_count: int


class UserProfilePublic(BaseModel):
    id: int
    username: str
    profile_image: str | None
    followers_count: int
    followings_count: int
    model_config = ConfigDict(from_attributes=True)


class UserProfilePrivate(UserProfilePublic):
    pass
