from __future__ import annotations

from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserReadSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    profile_image: str | None


class TokenInfoSchema(BaseModel):
    access_token: str
    token_type: str

