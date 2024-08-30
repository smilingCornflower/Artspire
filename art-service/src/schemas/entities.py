from pydantic import BaseModel, EmailStr


class BaseEntity(BaseModel):
    id: int


class UserEntity(BaseEntity):
    id: int
    username: str
    email: EmailStr
    profile_image: str | None


class TagEntity(BaseEntity):
    id: int
    name: str