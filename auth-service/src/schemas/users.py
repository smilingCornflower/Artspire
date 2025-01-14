from __future__ import annotations

from pydantic import EmailStr

from .base_ import CustomBaseModel


class UserCreateSchema(CustomBaseModel):
    username: str
    email: EmailStr
    password: str


class UserLoginSchema(CustomBaseModel):
    username: str
    password: str


class UserReadSchema(CustomBaseModel):
    id: int
    username: str
    email: EmailStr
    profile_image: str | None


class UserEntity(CustomBaseModel):
    id: int
    username: str
    hashed_password: str
    email: EmailStr
    profile_image: str | None

    role_id: int
    is_active: bool
    followers_count: int
    followings_count: int


class UserProfilePublic(CustomBaseModel):
    id: int
    username: str
    profile_image: str | None
    followers_count: int
    followings_count: int


class UserProfilePrivate(UserProfilePublic):
    pass
