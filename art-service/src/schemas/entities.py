from pydantic import EmailStr

from schemas.base import BaseEntity


class UserEntity(BaseEntity):
    id: int
    username: str
    email: EmailStr
    profile_image: str | None
    role_id: int = 1


class UsersToSavesEntity(BaseEntity):
    user_id: int
    art_id: int


class UsersToLikesEntity(BaseEntity):
    user_id: int
    art_id: int
