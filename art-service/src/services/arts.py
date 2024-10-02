# Standard libraries
from datetime import datetime, timezone, timedelta
import uuid
import shortuuid
from typing import TYPE_CHECKING

# External libraries
from google.cloud.exceptions import GoogleCloudError
from sqlalchemy.exc import SQLAlchemyError

# Local modules
from schemas.arts import ArtCreateSchema, ArtUploadSchema, ArtEntity
from bucket.s3_service import s3_service
from exceptions.http_exc import (
    ArtNotFoundHTTPException,
    InternalServerErrorHTTPException,
)
from config import logger

if TYPE_CHECKING:
    from repositories.arts import ArtRepository
    from repositories.art_to_tag import ArtToTagRepository
    from repositories.tags import TagRepository
    from fastapi import UploadFile
    from schemas.entities import TagEntity


class ArtsService:
    SIX_DAYS_IN_SECONDS: int = 6 * 24 * 3600
    UNDELETED_BLOB_NAMES_FILE: str = "undeleted_blob_names.txt"

    def __init__(
        self,
        art_repo: "ArtRepository",
        art_to_tag_repo: "ArtToTagRepository",
        tag_repo: "TagRepository",
    ) -> None:
        self.art_repo = art_repo
        self.art_to_tag_repo = art_to_tag_repo
        self.tag_repo = tag_repo

    async def _refresh_art_url_if_needed(self, art: "ArtEntity") -> "ArtEntity":
        """
        Refreshes the art URL if it is outdated.

        If the URL of the art is older than 6 days, a new URL is generated and the database entry
        is updated with the new URL and timestamp.

        :param art: The art entity to check and potentially update.
        :return: The updated art entity if the URL was refreshed.
        """
        generated_at_dt: datetime = art.url_generated_at
        current_dt: datetime = datetime.now(tz=timezone.utc)
        # With tzinfo it raises exceptions, IDK why, just don't touch it.
        current_dt: datetime = current_dt.replace(tzinfo=None)
        dt_diff_in_seconds: float = (current_dt - generated_at_dt).total_seconds()

        if dt_diff_in_seconds > self.SIX_DAYS_IN_SECONDS:
            try:
                art_new_url: str = s3_service.create_url(art.blob_name)
            except GoogleCloudError as err:
                logger.error("Error: {err}")
                raise InternalServerErrorHTTPException from err
            to_refresh: dict = {
                "url": art_new_url,
                "url_generated_at": current_dt,
            }
            new_art: "ArtEntity" = art.model_copy()
            new_art.url = art_new_url
            new_art.url_generated_at = current_dt
            try:
                await self.art_repo.update_one(model_id=art.id, data=to_refresh)
            except SQLAlchemyError as err:
                logger.error("Error: {err}")
                raise InternalServerErrorHTTPException from err
            return new_art
        return art

    async def _increase_views_count(self, art_id: int) -> None:
        await self.art_repo.change_counter(art_id, number=1, counter_name="views")

    async def add_art(
        self,
        art_data: "ArtUploadSchema",
        art_file: "UploadFile",
        create_tags: bool = False,
    ) -> int:
        """
        Adds an artwork to the repository, along with optional tag creation.

        This method handles the process of uploading an image file to S3 storage using
        `s3_service.upload_image()`. If the uploaded file is not a valid image,
        an `InvalidImageTypeHTTPException` is raised.

        After a successful upload, the method generates a URL for accessing the image, stores it in
        the database along with metadata from `art_data`, and returns the ID of the newly created
        art record.

        If `create_tags` is set to True, the method also handles tag creation and association of
        tags with the artwork. It first checks if the tags already exist, creates any missing tags,
        and links them to the newly created artwork.

        param art_data: The data related to the artwork, including user ID, title, and tags.
        param art_file: The file object representing the artwork image to be uploaded.
        param create_tags: If True, the method will create and associate tags with the artwork.
        return: The ID of the newly created artwork record in the database.
        raises InvalidImageTypeHTTPException: If the uploaded file is not a valid image.
        raises InternalServerErrorHTTPException: If there is an error during the database operation.
        """
        logger.warning("STARTED add_art()")
        blob_name: str = await s3_service.upload_image(
            image_file=art_file, user_id=art_data.user_id
        )
        art_url: str = s3_service.create_url(blob_name=blob_name)
        url_generated_dt: datetime = datetime.now(tz=timezone.utc)
        url_generated_dt: datetime = url_generated_dt.replace(tzinfo=None)

        art_create_data: "ArtCreateSchema" = ArtCreateSchema(
            user_id=art_data.user_id,
            title=art_data.title,
            url=art_url,
            blob_name=blob_name,
            url_generated_at=url_generated_dt,
        )
        tag_names: list[str] = art_data.tags
        try:
            logger.info(f"await self.art_repo.add_one(art_create_data.model_dump())")
            new_art_id: int = await self.art_repo.add_one(art_create_data.model_dump())
            if create_tags:
                tag_names_to_add_data: list[dict] = [
                    {"name": name} for name in tag_names
                ]
                logger.info(
                    f"await self.tag_repo.add_one({tag_names_to_add_data}, ['name'])"
                )
                await self.tag_repo.add_one(
                    data=tag_names_to_add_data, ignore_conflicts=["name"]
                )

            tag_entities: list = await self.tag_repo.find_all({"name": tag_names})
            art_to_tag_add_data: list[dict] = [
                {"art_id": new_art_id, "tag_id": tag_entity.id}
                for tag_entity in tag_entities
            ]
            logger.info(f"await self.art_to_tag_repo.add_one({art_to_tag_add_data}")
            await self.art_to_tag_repo.add_one(art_to_tag_add_data)
        except SQLAlchemyError as err:
            logger.critical(f"Error: {err}")
            raise InternalServerErrorHTTPException from err
        return new_art_id

    async def get_arts(
        self,
        art_id: int | None = None,
        offset: int | None = None,
        limit: int | None = None,
        include_tags: bool = False,
    ) -> "list[ArtEntity]":
        """
        Retrieves a list of arts, optionally filtered by ID.

        If `art_id` is provided, retrieves the art with that ID. Otherwise, retrieves all arts.
        The URLs of the arts are refreshed if they are outdated.

        param art_id: The ID of the art to retrieve, or None to get all arts.
        param offset: The number of arts to skip, for pagination.
        param limit: The maximum number of arts to return.
        return: A list of `ArtEntity` objects.
        raises ArtNotFoundHTTPException: If no arts are found.
        raises InternalServerErrorHTTPException: If there is an error.
        """
        logger.warning(f"Started get_arts()")
        if art_id:
            filter_condition: dict = {"id": art_id}
            await self._increase_views_count(art_id)
        else:
            filter_condition: dict = {}
        try:
            art_attributes: list[str] | None = None
            if include_tags:
                art_attributes = ["tags"]

            # noinspection PyTypeChecker
            all_arts: list["ArtEntity"] = await self.art_repo.find_all(
                filter_by=filter_condition,
                offset=offset,
                limit=limit,
                joined_attributes=art_attributes,
            )
        except SQLAlchemyError as err:
            logger.error(f"Error: {err}")
            raise InternalServerErrorHTTPException from err

        if not all_arts:
            raise ArtNotFoundHTTPException(detail="No art found")

        result_arts: "list[ArtEntity]" = []
        for art in all_arts:
            refreshed_art: "ArtEntity" = await self._refresh_art_url_if_needed(art)
            result_arts.append(refreshed_art)
        logger.info(f"Finished get_arts()")
        return result_arts

    async def delete_art(self, art_id: int) -> bool:
        """
        Deletes an art by its ID from the database and S3 storage.

        First, checks if the art exists in the database. If found, deletes the art record
        from the database and attempts to delete the associated file from S3 storage.
        If the file deletion fails, the blob name is recorded in the `UNDELETED_BLOB_NAMES_FILE`.

        :param art_id: The ID of the art to be deleted.
        :return: True if the art was deleted, False if the art was not found.
        :raises InternalServerErrorHTTPException: If there is a database error.
        """
        try:
            # noinspection PyTypeChecker
            art_entities: list["ArtEntity"] = await self.art_repo.find_all(
                {"id": art_id}
            )
            if not art_entities:
                return False
        except SQLAlchemyError as err:
            raise InternalServerErrorHTTPException from err

        art_entity: "ArtEntity" = art_entities[0]
        try:
            await self.art_repo.delete_one({"id": art_id})
        except SQLAlchemyError as err:
            logger.error(f"Error: {err}")
            raise InternalServerErrorHTTPException from err
        try:
            s3_service.delete_file(blob_name=art_entity.blob_name)
        except GoogleCloudError as err:
            logger.error(f"Error {err}")
            with open(self.UNDELETED_BLOB_NAMES_FILE, mode="a", encoding="utf-8") as f:
                f.write(f"{art_entity.blob_name}\n")

        return True
