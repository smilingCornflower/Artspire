from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from config import settings


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )
