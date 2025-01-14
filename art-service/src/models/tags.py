from sqlalchemy import String
from sqlalchemy.orm import Mapped as M, mapped_column as mc, relationship

from database.base import Base
from schemas.tags import TagEntity


class TagOrm(Base):
    __tablename__ = "tags"

    id: M[int] = mc(primary_key=True)
    name: M[str] = mc(String(255), unique=True, nullable=False)

    arts: M[int] = relationship("ArtOrm", secondary="arts_to_tags", back_populates="tags")

    def to_entity(self) -> "TagEntity":
        tag_entity: "TagEntity" = TagEntity(
            id=self.id,
            name=self.name,
        )
        return tag_entity
