from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

art_to_tag = Table(
    "arts_to_tags",
    Base.metadata,
    Column("art_id", Integer, ForeignKey("arts.id", ondelete="CASCADE"), nullable=False),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
)
