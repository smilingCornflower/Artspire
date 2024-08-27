from repositories.repository import SQLAlchemyRepository
from models.arts import ArtOrm


class ArtRepository(SQLAlchemyRepository):
    model = ArtOrm
