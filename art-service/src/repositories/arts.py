from repositories.repository import SQLAlchemyRepository
from .tags import TagRepository
from models.arts import ArtOrm
from .tags import TagRepository
from config import logger
from database.db import db_manager
from sqlalchemy.exc import SQLAlchemyError
from schemas.entities import TagEntity
from sqlalchemy import select
from models.tags import TagOrm
from .art_to_tag import ArtToTagRepository
from schemas.arts import ArtCreateSchema


class ArtRepository(SQLAlchemyRepository):
    model = ArtOrm

    async def add_art(self, art_data: "ArtCreateSchema") -> int:
        art_to_tag_repo: "ArtToTagRepository" = ArtToTagRepository()
        tag_repo: "TagRepository" = TagRepository()

        art_data: dict = art_data.to_dict()
        tag_names: list[str] = art_data.pop("tags", [])
        try:
            logger.info(f"Attempting to add new art with data: {art_data}")
            new_art_id: int = await self.add_one(art_data)
            logger.info(f"Successfully added new art with ID: {new_art_id}")
        except SQLAlchemyError as err:
            logger.error(f"Error adding new art: {err}")
            raise

        for tag_name in tag_names:
            try:
                tag_entity: list = await tag_repo.find_all({"name": tag_name})
                if tag_entity:
                    tag_entity: "TagEntity" = tag_entity[0]
                    tag_id: int = tag_entity.id
                    logger.info(f"Adding tag '{tag_name}' with ID {tag_id} to art ID {new_art_id}")
                    await art_to_tag_repo.add_one(
                        {"art_id": new_art_id, "tag_id": tag_id}
                    )
                else:
                    logger.warning(f"Tag '{tag_name}' not found, skipping")
            except SQLAlchemyError as err:
                logger.error(f"Error adding tag '{tag_name}' to art ID {new_art_id}: {err}")
                raise
        return new_art_id
