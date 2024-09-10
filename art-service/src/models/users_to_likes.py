from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as mc
from sqlalchemy import ForeignKey
from database.base import Base


class UsersToLikesOrm(Base):
    __tablename__ = "users_to_likes"

    user_id: M[int] = mc(primary_key=True)
    art_id: M[int] = mc(ForeignKey("arts.id"), primary_key=True)

