from services.arts import ArtsService
from repositories.arts import ArtRepository


def get_art_service() -> "ArtsService":
    return ArtsService(art_repo=ArtRepository())
