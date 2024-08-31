from pydantic import BaseModel, EmailStr


class BaseEntity(BaseModel):
    id: int


class UserEntity(BaseEntity):
    id: int
    username: str
    email: EmailStr
    profile_image: str | None
    role_id: int = 1


class TagEntity(BaseEntity):
    id: int
    name: str