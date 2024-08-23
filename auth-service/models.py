from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as mc

from sqlalchemy import (
    MetaData, String, DateTime, ForeignKey, func
)
from config import settings
import datetime


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention=settings.naming_convention,
    )


class RoleOrm(Base):
    __tablename__ = "roles"

    id: M[int] = mc(primary_key=True)
    name: M[str] = mc(String(length=50), unique=True, nullable=False)

    users = relationship("UserOrm", back_populates="role")


class UserOrm(Base):
    __tablename__ = "users"

    id: M[int] = mc(primary_key=True)

    username: M[str] = mc(String(length=50), unique=True, nullable=False)
    email: M[str] = mc(String(length=255), unique=True, nullable=False)
    hashed_password: M[str] = mc(String(length=64), unique=False, nullable=False)
    role_id: M[int] = mc(ForeignKey("roles.id"), nullable=False)

    is_active: M[bool] = mc(default=True, nullable=False)
    is_verified: M[bool] = mc(default=False, nullable=False)

    profile_image: M[str] = mc(String(255), nullable=True)

    created_at: M[datetime] = mc(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    role = relationship("RoleOrm", back_populates="users")
