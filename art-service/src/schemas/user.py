from pydantic import EmailStr
from .base import BaseEntity


class UserEntity(BaseEntity):
    id: int
    username: str
    email: EmailStr
    profile_image: str | None
    role_id: int = 1


