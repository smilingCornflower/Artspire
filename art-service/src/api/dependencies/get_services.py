from typing import TYPE_CHECKING

from fastapi import Depends

from database.db import db_manager
from repositories.art_to_tag import ArtToTagRepository
from repositories.arts import ArtRepository
from repositories.comments import CommentsRepository
from repositories.tags import TagRepository
from repositories.users_to_likes import UsersToLikesRepository
from repositories.users_to_saves import UsersToSavesRepository
from services.arts import ArtsService
from services.comments import CommentsService
from services.tags import TagsService
from services.users_to_likes import UsersToLikesService
from services.users_to_saves import UsersToSavesService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> "AsyncSession":
    async with db_manager.async_session_maker() as session:
        yield session


class DBGateway:
    def __init__(self, session: "AsyncSession"):
        self.session = session

    def get_arts_service(self) -> ArtsService:
        return ArtsService(
            art_repo=ArtRepository(self.session),
            art_to_tag_repo=ArtToTagRepository(self.session),
            tag_repo=TagRepository(self.session),
            user_to_likes_repo=UsersToLikesRepository(self.session),
        )

    def get_tags_service(self) -> TagsService:
        return TagsService(
            tag_repo=TagRepository(self.session),
        )

    def get_users_to_saves_service(self) -> UsersToSavesService:
        return UsersToSavesService(
            users_to_saves_repo=UsersToSavesRepository(self.session),
            art_repo=ArtRepository(self.session),
        )

    def get_users_to_likes_service(self) -> UsersToLikesService:
        return UsersToLikesService(
            users_to_likes_repo=UsersToLikesRepository(self.session),
            art_repo=ArtRepository(self.session),
        )

    def get_comments_service(self) -> CommentsService:
        return CommentsService(
            comments_repo=CommentsRepository(self.session),
            art_repo=ArtRepository(self.session),
        )


async def get_db_gateway(
        session: "AsyncSession" = Depends(get_session),
) -> DBGateway:
    return DBGateway(session)
