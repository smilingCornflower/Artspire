from database.base import Base
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as mc
from sqlalchemy import String
from sqlalchemy.orm import relationship


class RoleOrm(Base):
    __tablename__ = "roles"

    id: M[int] = mc(primary_key=True)
    name: M[str] = mc(String(length=50), unique=True, nullable=False)

    users = relationship("UserOrm", back_populates="role")
