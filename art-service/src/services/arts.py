# Standard libraries
from datetime import datetime, timezone, timedelta
import uuid
import shortuuid
from typing import TYPE_CHECKING

# External libraries
from google.cloud.exceptions import GoogleCloudError
from sqlalchemy.exc import SQLAlchemyError

# Local modules
from schemas.arts import ArtCreateSchema, ArtUploadSchema
from utils.img import convert_to_jpg
from bucket.s3_client import s3_client
from exceptions.http_exc import (
    FailedUploadHttpException,
    ArtNotFoundHTTPException,
    InternalServerErrorHTTPException,
)
from config import logger

if TYPE_CHECKING:
    from repositories.arts import ArtRepository
    from schemas.entities import ArtEntity
    from fastapi import UploadFile
    from typing import BinaryIO

UNDELETED_BLOB_NAMES_FILE: str = "undeleted_blob_names.txt"


class ArtsService:
    """
    Service class for managing art operations, including adding, retrieving, and deleting arts.

    Attributes:
        IMG_TYPES (tuple[str]): Supported image MIME types for art uploads (e.g., JPEG, PNG, WEBP).
        JPEG (str): The MIME type for JPEG images.
        art_repo (ArtRepository): Repository for performing database operations related to arts.
    """
    IMG_TYPES: tuple[str] = ("image/jpeg", "image/png", "image/webp")
    JPEG: str = "image/jpeg"

    def __init__(self, art_repo: "ArtRepository"):
        """
        Initializes the ArtsService with the provided repository.

        @param art_repo: The repository interface for interacting with art data.
        """
        self.art_repo = art_repo
        logger.info(f"Initialized ArtsService with repository: {self.art_repo}")

    async def add_art(self,
                      art_data: "ArtUploadSchema",
                      art_file: "UploadFile",
                      ) -> int:
        """
        Adds a new art to the repository.

        If the uploaded image is in a format other than JPEG, it is converted to JPEG before uploading.
        The image is uploaded to cloud storage, and its URL is saved along with art metadata.

        @param art_data: Metadata for the art, including user ID, title, and tags.
        @param art_file: The uploaded image file. Supported formats are defined by `IMG_TYPES`.
        @return: The ID of the newly created art in the repository.
        @raises FailedUploadHttpException: If the image upload to cloud storage fails.
        @raises InternalServerErrorHTTPException: If an unexpected error occurs during the process.
        """
        art_type: str = art_file.content_type
        image_file: "BinaryIO" = art_file.file

        logger.debug(f"art_type: {art_type}")

        if art_type in self.IMG_TYPES and art_type != self.JPEG:
            logger.info("Converting image to JPEG")
            image_file = await convert_to_jpg(art_file.file)
        try:
            image_name: str = f"arts/{art_data.user_id}/{shortuuid.uuid()}.jpg"
            logger.info(f"image_name: {image_name}")
            blob_name: str = s3_client.upload_file(file_obj=image_file, blob_name=image_name)
            logger.info(f"blob_name: {blob_name}")
        except GoogleCloudError as err:
            logger.error(f"GoogleCloudError occurred during file upload: {err}")
            raise FailedUploadHttpException from err
        art_url: str = s3_client.create_url(blob_name=blob_name)
        art_url_dt: datetime = datetime.now(tz=timezone.utc)
        art_url_dt: datetime = art_url_dt.replace(tzinfo=None)
        art_to_create_data: "ArtCreateSchema" = ArtCreateSchema(
            user_id=art_data.user_id,
            title=art_data.title,
            tags=art_data.tags,
            url=art_url,
            blob_name=image_name,
            url_generated_at=art_url_dt,
        )
        logger.debug(f"art_url: {art_url}")
        logger.debug(f"art_url_dt: {art_url_dt}")
        logger.debug(f"art_to_create_data: {art_to_create_data}")
        try:
            new_art_id: int = await self.art_repo.add_art(art_to_create_data)
            logger.info("Art data successfully added to repository")
        except SQLAlchemyError as err:
            logger.error(f"SQLAlchemyError occurred during adding art data to repository: {err}")
            raise FailedUploadHttpException from err
        except Exception as err:
            logger.error(f"Unexpected error occurred: {err}", exc_info=True)
            raise InternalServerErrorHTTPException(detail="An unexpected error occurred")
        return new_art_id

    async def get_arts(self, art_id: int | None = None) -> "list[ArtEntity]":
        """
        Retrieves arts from the repository.

        If an `art_id` is provided, retrieves the specific art with that ID. If no ID is provided, retrieves all arts.
        Updates the URL of arts if the URL has expired (older than 6 days).

        @param art_id: Optional ID of the art to retrieve. If None, retrieves all arts.
        @return: A list of `ArtEntity` objects representing the retrieved arts.
        @raises ArtNotFoundHTTPException: If no art is found with the specified ID.
        @raises InternalServerErrorHTTPException: If a database error occurs during retrieval or update.
        """
        logger.info(f"get_arts called with art_id: {art_id}")
        try:
            filter_condition: dict = {}
            if art_id:
                filter_condition = {"id": art_id}
                logger.debug(f"Filter condition set to: {filter_condition}")

            logger.debug("Fetching all arts from repository")
            # noinspection PyTypeChecker
            all_arts: list["ArtEntity"] = await self.art_repo.find_all(filter_condition)
            logger.debug(f"Fetched arts: {all_arts}")

            if not all_arts:
                logger.warning("No arts found, raising ArtNotFoundHTTPException")
                raise ArtNotFoundHTTPException(detail="No art found with the given ID")

            result_arts: "list[ArtEntity]" = []

            for art in all_arts:
                generated_at_dt: datetime = art.url_generated_at
                current_dt: datetime = datetime.now(tz=timezone.utc)
                current_dt: datetime = current_dt.replace(tzinfo=None)
                logger.debug(f"Processing art with id: {art.id}")
                logger.debug(f"URL generated at: {generated_at_dt}")
                logger.debug(f"Current datetime: {current_dt}")

                dt_diff_in_seconds: float = (current_dt - generated_at_dt).total_seconds()
                logger.debug(f"Time difference (seconds): {dt_diff_in_seconds}")

                if dt_diff_in_seconds > 86400 * 6:
                    logger.info(f"Updating URL for art id: {art.id}")
                    art_new_url: str = s3_client.create_url(art.blob_name)
                    to_update: dict = {
                        "url": art_new_url,
                        "url_generated_at": current_dt,
                    }
                    art.url = art_new_url
                    art.url_generated_at = current_dt

                    try:
                        await self.art_repo.update_one(model_id=art.id, data=to_update)
                        logger.debug(f"Updated art id: {art.id} with new URL and datetime")
                    except SQLAlchemyError as err:
                        logger.error(f"Error occurred while updating art id: {art.id} - {err}")
                        raise InternalServerErrorHTTPException(
                            detail="An unexpected database error occurred")

                result_arts.append(art)

            logger.info(f"Returning result arts: {result_arts}")
            return result_arts

        except SQLAlchemyError as err:
            logger.error(f"Database error occurred: {err}", exc_info=True)
            raise InternalServerErrorHTTPException(detail="An unexpected database error occurred")
        except Exception as err:
            logger.error(f"Unexpected error occurred: {err}", exc_info=True)
            raise InternalServerErrorHTTPException(detail="An unexpected error occurred")

    async def del_art(self, art_id: int):
        """
        Deletes an art from the repository by its ID.

        Attempts to delete the specified art from the repository first. If the deletion from the repository is successful,
        it then attempts to delete the art from cloud storage. If the cloud deletion fails, the blob name is recorded
        in a file for subsequent retry. If the art is not found or has already been deleted, returns `False`.

        @param art_id: The ID of the art to delete.
        @return: `True` if the art was successfully deleted from both the repository and cloud storage; `False` if it was not found or already deleted.
        @raises InternalServerErrorHTTPException: If a database error occurs during deletion from the repository.
        """
        logger.info(f"Attempting to delete art with id: {art_id}")
        try:
            # noinspection PyTypeChecker
            art_entities: list["ArtEntity"] = await self.art_repo.find_all({"id": art_id})
        except SQLAlchemyError as err:
            logger.error(f"Database error while finding art with id: {art_id}, error: {err}")
            raise InternalServerErrorHTTPException(f"Failed to delete art with id: {art_id}")

        if not art_entities:
            logger.warning(f"Art with id: {art_id} not found or already deleted.")
            return False

        art_entity: "ArtEntity" = art_entities[0]

        try:
            await self.art_repo.delete_one(object_id=art_id)
            logger.info(f"Successfully deleted art with id: {art_id}")
        except SQLAlchemyError as err:
            logger.error(f"Failed to delete art with id: {art_id}, error: {err}")
            raise InternalServerErrorHTTPException

        try:
            await s3_client.delete_file(blob_name=art_entity.blob_name)
        except GoogleCloudError as err:
            logger.error(f"Failed to delete art with id: {art_id} from cloud storage, error: {err}")
            with open(UNDELETED_BLOB_NAMES_FILE, mode='a', encoding='utf-8') as f:
                f.write(f"{art_entity.blob_name}\n")

        return True