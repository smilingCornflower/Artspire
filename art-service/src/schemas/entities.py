from pydantic import BaseModel, EmailStr


class BaseEntity(BaseModel):
    ...


class UserEntity(BaseEntity):
    id: int
    username: str
    email: EmailStr
    profile_image: str | None
    role_id: int = 1


class TagEntity(BaseEntity):
    id: int
    name: str


class UsersToSavesEntity(BaseEntity):
    user_id: int
    art_id: int


class UsersToLikesEntity(BaseEntity):
    user_id: int
    art_id: int
