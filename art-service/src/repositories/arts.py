# SQLAlchemy
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Local
from config import logger
from database.db import db_manager
from models.arts import ArtOrm
from models.tags import TagOrm
from repositories.repository import SQLAlchemyRepository
from schemas.arts import ArtCreateSchema
from schemas.entities import TagEntity

from .art_to_tag import ArtToTagRepository
from .tags import TagRepository


class ArtRepository(SQLAlchemyRepository):
    model = ArtOrm

    async def add_art(self, art_data: "ArtCreateSchema", create_tags: bool = False) -> int:
        art_to_tag_repo: "ArtToTagRepository" = ArtToTagRepository()
        tag_repo: "TagRepository" = TagRepository()
        art_data: dict = art_data.dict()
        tag_names: list[str] = art_data.pop("tags", [])

        logger.debug(f"Adding new art with data: {art_data}")
        try:
            new_art_id: int = await self.add_one(art_data)
            logger.info(f"New art added with ID: {new_art_id}")
        except SQLAlchemyError as err:
            logger.error(f"SQLAlchemyError: {err}")
            raise

        for tag_name in tag_names:
            try:
                logger.debug(f"Processing tag: {tag_name}")
                if create_tags:
                    try:
                        await tag_repo.add_one({"name": tag_name})
                        logger.debug(f"Tag '{tag_name}' created")
                    except IntegrityError as err:
                        logger.error(
                            f"Expected IntegrityError while creating tag '{tag_name}': {err}")
                        pass  # Ignoring the error as the tag might already exist

                tag_entity: list = await tag_repo.find_all({"name": tag_name})
                if tag_entity:
                    tag_entity: "TagEntity" = tag_entity[0]
                    tag_id: int = tag_entity.id
                    await art_to_tag_repo.add_one({"art_id": new_art_id, "tag_id": tag_id})

                    logger.info(f"Art ID {new_art_id} linked with tag '{tag_name}' (ID: {tag_id})")
                else:
                    logger.warning(f"Tag '{tag_name}' not found, skipping")
            except SQLAlchemyError as err:
                logger.error(f"SQLAlchemyError: {err}")
                raise

        return new_art_id

