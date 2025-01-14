from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped as M, mapped_column as mc, relationship

from database.base import Base
from schemas.user_to_likes import UsersToLikesEntity


class UsersToLikesOrm(Base):
    __tablename__ = "users_to_likes"

    user_id: M[int] = mc(primary_key=True)
    art_id: M[int] = mc(ForeignKey("arts.id", ondelete="CASCADE"), primary_key=True)

    art = relationship("ArtOrm", back_populates="likes")

    def to_entity(self) -> UsersToLikesEntity:
        entity: "UsersToLikesEntity" = UsersToLikesEntity(
            user_id=self.user_id,
            art_id=self.art_id
        )
        return entity
