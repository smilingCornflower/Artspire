from repositories.users_to_saves import UsersToSavesRepository
from repositories.arts import ArtRepository
from services.users_to_saves import UsersToSavesService


def get_users_to_saves_service() -> "UsersToSavesService":
    return UsersToSavesService(
        users_to_service_repo=UsersToSavesRepository(),
        art_repo=ArtRepository(),
    )
