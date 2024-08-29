from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as mc
from sqlalchemy.orm import relationship
from sqlalchemy import (
    String,
    ForeignKey,
    Integer,
    DateTime,
    func,
)
from database.base import Base
from datetime import datetime


class ArtOrm(Base):
    __tablename__ = 'arts'

    id: M[int] = mc(primary_key=True)
    user_id: M[int]
    blob_name: M[str] = mc(String(length=128), unique=True, nullable=False)
    url: M[str] = mc(String(length=2048), unique=True, index=True, nullable=False)
    url_generated_at: M[datetime]

    title: M[str] = mc(String(length=256), nullable=True)
    likes_count: M[int] = mc(default=0)

    tags = relationship("TagOrm", secondary="arts_to_tags", back_populates="arts")

    created_at: M[datetime] = mc(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
