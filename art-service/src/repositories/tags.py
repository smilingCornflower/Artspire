from .repository import SQLAlchemyRepository
from models.tags import TagOrm


class TagRepository(SQLAlchemyRepository):
    model = TagOrm