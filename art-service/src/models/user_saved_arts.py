from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as mc
from sqlalchemy import ARRAY, Integer
from database.base import Base
from schemas.entities import UserSavedArtsEntity


class UserSavedArtsOrm(Base):
    __tablename__ = "user_saved_arts"

    id: M[int] = mc(primary_key=True, index=True)
    arts: M[list[int]] = mc(ARRAY(Integer), nullable=True)

    def to_entity(self) -> "UserSavedArtsEntity":
        user_saved_arts_entity = UserSavedArtsEntity(
            id=self.id,
            arts=self.arts,
        )
        return user_saved_arts_entity
