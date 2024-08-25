from database.base import Base
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as mc

from sqlalchemy import (
    String, ForeignKey, DateTime, func
)
from sqlalchemy.orm import relationship

from roles import RoleOrm

from schemas.users import UserEntity


class UserOrm(Base):
    __tablename__ = "users"

    id: M[int] = mc(primary_key=True)

    username: M[str] = mc(String(length=50), unique=True, nullable=False)
    email: M[str] = mc(String(length=255), unique=True, nullable=False)
    hashed_password: M[str] = mc(String(length=64), unique=False, nullable=False)
    role_id: M[int] = mc(ForeignKey("roles.id"), default=1, server_default=1, nullable=False)

    is_active: M[bool] = mc(default=True, nullable=False)
    is_verified: M[bool] = mc(default=False, nullable=False)

    profile_image: M[str] = mc(String(255), nullable=True)

    created_at: M[datetime] = mc(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    role = relationship("RoleOrm", back_populates="users")

    def to_entity(self) -> UserEntity:
        user_entity = UserEntity(
            id=self.id,
            username=self.username,
            email=self.email,
            profile_image=self.profile_image,
            role_id=self.is_active,
            is_active=self.is_active,
        )
        return user_entity
