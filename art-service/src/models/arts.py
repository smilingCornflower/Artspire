from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as mc
from sqlalchemy.orm import relationship
from sqlalchemy import (
    String,
    ForeignKey,
    Integer,
    DateTime,
    func,
    text,
)
from sqlalchemy.exc import MissingGreenlet
from database.base import Base
from datetime import datetime
from schemas.arts import ArtEntity
from config import logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tags import TagOrm


class ArtOrm(Base):
    __tablename__ = "arts"

    id: M[int] = mc(primary_key=True)
    user_id: M[int] = mc(nullable=False)
    blob_name: M[str] = mc(String(length=128), unique=True, nullable=False)
    url: M[str] = mc(String(length=2048), unique=True, index=True, nullable=False)
    url_generated_at: M[datetime]

    title: M[str] = mc(String(length=256), nullable=True)

    likes_count: M[int] = mc(default=0, server_default=text("0"), nullable=False)
    views_count: M[int] = mc(default=0, server_default=text("0"), nullable=False)

    tags = relationship("TagOrm", secondary="arts_to_tags", back_populates="arts")
    likes = relationship("UsersToLikesOrm", back_populates="art", cascade="all, delete")
    saves = relationship("UsersToSavesOrm", back_populates="art", cascade="all, delete")

    created_at: M[datetime] = mc(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def to_entity(self) -> "ArtEntity":
        art_entity: "ArtEntity" = ArtEntity(
            id=self.id,
            user_id=self.user_id,
            blob_name=self.blob_name,
            url=self.url,
            url_generated_at=self.url_generated_at,
            title=self.title,
            likes_count=self.likes_count,
            views_count=self.views_count,
            created_at=self.created_at,
        )
        try:
            tags_info: list = [tag.to_entity() for tag in self.tags]
            art_entity.tags = tags_info
        except MissingGreenlet:
            pass

        return art_entity
