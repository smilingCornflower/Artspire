from services.arts import ArtsService
from repositories.arts import ArtRepository


def get_arts_service() -> "ArtsService":
    return ArtsService(art_repo=ArtRepository())
