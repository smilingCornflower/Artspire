from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as mc
from sqlalchemy import ForeignKey

from database.base import Base


class SubscriptionOrm(Base):
    __tablename__ = "subscriptions"

    follower_id: M[int] = mc(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    artist_id: M[int] = mc(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
