from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as mc
from sqlalchemy import ForeignKey
from database.base import Base
from schemas.entities import UsersToLikesEntity


class UsersToLikesOrm(Base):
    __tablename__ = "users_to_likes"

    user_id: M[int] = mc(primary_key=True)
    art_id: M[int] = mc(ForeignKey("arts.id"), primary_key=True)

    def to_entity(self) -> UsersToLikesEntity:
        entity: "UsersToLikesEntity" = UsersToLikesEntity(
            user_id=self.user_id,
            art_id=self.art_id
        )
        return entity
