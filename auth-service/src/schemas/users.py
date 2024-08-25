from __future__ import annotations

from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLoginSchema(BaseModel):
    username: str
    password: str


class UserEntity(BaseModel):
    id: int
    username: str
    hashed_password: str
    email: EmailStr
    profile_image: str | None

    role_id: bool
    is_active: bool
