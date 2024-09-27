# id, user_id, art_id, text, likes_count, dislikes_count
# is_edited, published_dt, parent_id

from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as mc
from sqlalchemy import ForeignKey, String, DateTime, func
from database.base import Base

from schemas.comments import CommentEntity
from datetime import datetime


class CommentOrm(Base):
    __tablename__ = "comments"

    id: M[int] = mc(primary_key=True)
    user_id: M[int] = mc(nullable=False)
    art_id: M[int] = mc(ForeignKey("arts.id"), nullable=False)
    text: M[str] = mc(String(512), nullable=False)
    likes_count: M[int] = mc(default=0, nullable=False)
    dislikes_count: M[int] = mc(default=0, nullable=False)
    is_edited: M[bool] = mc(default=False, nullable=False)

    created_at: M[datetime] = mc(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def to_entity(self) -> "CommentEntity":
        comment_entity = CommentEntity(
            id=self.id,
            user_id=self.user_id,
            art_id=self.art_id,
            text=self.text,
            likes_count=self.likes_count,
            dislikes_count=self.dislikes_count,
            is_edited=self.is_edited,
            created_at=self.created_at,
        )
        return comment_entity
