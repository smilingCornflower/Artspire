from sqlalchemy.exc import SQLAlchemyError

from repositories.tags import TagRepository
from exceptions.http_exc import InternalServerErrorHTTPException
from schemas.entities import TagEntity
from config import logger


class TagsService:
    def __init__(self, tag_repo: "TagRepository"):
        self.tag_repo: "TagRepository" = tag_repo

    async def add_tag(self, tag_name: str) -> int:
        new_tag_data: dict = {"name": tag_name}
        try:
            new_tag_id: int = await self.tag_repo.add_one(data=new_tag_data)
        except SQLAlchemyError as err:
            logger.error(f"Failed to add tag '{tag_name}': {err}")
            raise InternalServerErrorHTTPException from err
        return new_tag_id

    async def delete_tag(self, tag_id: int) -> bool:
        try:
            tag_delete_result: bool = await self.tag_repo.delete_one(item_id=tag_id)
        except SQLAlchemyError as err:
            logger.error(f"Failed to delete tag with id {tag_id}: {err}")
            raise InternalServerErrorHTTPException
        return tag_delete_result

    async def get_tags(self) -> list:
        try:
            all_tags: list = await self.tag_repo.find_all({})
        except SQLAlchemyError as err:
            logger.error(f"Failed to get tags {err}")
            raise InternalServerErrorHTTPException
        return all_tags
