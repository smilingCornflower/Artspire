from repositories.arts import ArtRepository
from repositories.tags import TagRepository
from repositories.users_to_saves import UsersToSavesRepository
from repositories.users_to_likes import UsersToLikesRepository
from repositories.comments import CommentsRepository
from repositories.art_to_tag import ArtToTagRepository

from services.arts import ArtsService
from services.tags import TagsService
from services.users_to_saves import UsersToSavesService
from services.users_to_likes import UsersToLikesService
from services.comments import CommentsService

from database.db import db_manager


async def get_arts_service() -> "ArtsService":
    return ArtsService(
        art_repo=ArtRepository(db_manager.async_session_maker()),
        art_to_tag_repo=ArtToTagRepository(db_manager.async_session_maker()),
        tag_repo=TagRepository(db_manager.async_session_maker()),
    )


async def get_tags_service() -> "TagsService":
    return TagsService(TagRepository(db_manager.async_session_maker()))


async def get_users_to_saves_service() -> "UsersToSavesService":
    return UsersToSavesService(
        users_to_saves_repo=UsersToSavesRepository(db_manager.async_session_maker()),
        art_repo=ArtRepository(db_manager.async_session_maker()),
    )


async def get_users_to_likes_servcie() -> "UsersToLikesService":
    return UsersToLikesService(
        users_to_likes_repo=UsersToLikesRepository(db_manager.async_session_maker()),
        art_repo=ArtRepository(db_manager.async_session_maker()),
    )


async def get_comments_service() -> "CommentsService":
    return CommentsService(
        comments_repo=CommentsRepository(db_manager.async_session_maker()),
        art_repo=ArtRepository(db_manager.async_session_maker()),
    )
