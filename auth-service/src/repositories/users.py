from repositories.repository import SQLAlchemyRepository
from models.users import UserOrm


class UserRepository(SQLAlchemyRepository):
    model = UserOrm
