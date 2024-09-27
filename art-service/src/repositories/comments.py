from .repository import SQLAlchemyRepository
from models.comments import CommentOrm


class CommentsRepository(SQLAlchemyRepository):
    model = CommentOrm
