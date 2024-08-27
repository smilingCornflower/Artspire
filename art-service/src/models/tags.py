from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as mc
from sqlalchemy.orm import relationship
from sqlalchemy import String, ForeignKey
from database.base import Base


class TagOrm(Base):
    __tablename__ = "tags"

    id: M[int] = mc(primary_key=True)
    name: M[str] = mc(String(255), unique=True, nullable=False)

    arts: M[int] = relationship("ArtOrm", secondary="arts_to_tags", back_populates="tags")
