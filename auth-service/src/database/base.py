from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from config import settings


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention=settings.naming_convention,
    )
