from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped as M, mapped_column as mc, relationship

from database.base import Base
from schemas.user_to_saves import UsersToSavesEntity


class UsersToSavesOrm(Base):
    __tablename__ = "users_to_saves"

    user_id: M[int] = mc(primary_key=True)
    art_id: M[int] = mc(ForeignKey("arts.id", ondelete="CASCADE"), primary_key=True)

    art = relationship("ArtOrm", back_populates="saves")

    def to_entity(self) -> "UsersToSavesEntity":
        entity = UsersToSavesEntity(
            user_id=self.user_id,
            art_id=self.art_id,
        )
        return entity
