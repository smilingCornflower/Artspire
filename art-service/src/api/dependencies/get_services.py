from repositories.arts import ArtRepository
from repositories.tags import TagRepository
from repositories.users_to_saves import UsersToSavesRepository
from repositories.users_to_likes import UsersToLikesRepository

from services.arts import ArtsService
from services.tags import TagsService
from services.users_to_saves import UsersToSavesService
from services.users_to_likes import UsersToLikesService


def get_arts_service() -> "ArtsService":
    return ArtsService(art_repo=ArtRepository())


def get_tags_service() -> "TagsService":
    return TagsService(TagRepository())


def get_users_to_saves_service() -> "UsersToSavesService":
    return UsersToSavesService(
        users_to_saves_repo=UsersToSavesRepository(),
        art_repo=ArtRepository(),
    )


def get_users_to_likes_servcie() -> "UsersToLikesService":
    return UsersToLikesService(
        users_to_likes_repo=UsersToLikesRepository(),
        art_repo=ArtRepository(),
    )
