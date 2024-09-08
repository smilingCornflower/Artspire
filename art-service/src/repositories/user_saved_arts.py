from .repository import SQLAlchemyRepository
from models.user_saved_arts import UserSavedArtsOrm


class UserSavedArtsRepository(SQLAlchemyRepository):
    model = UserSavedArtsOrm

