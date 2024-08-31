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


class ArtsService:
    IMG_TYPES: tuple[str] = ("image/jpeg", "image/png", "image/webp")
    JPEG: str = "image/jpeg"

    def __init__(self, art_repo: "ArtRepository"):
        self.art_repo = art_repo
        logger.info(f"Initialized ArtsService with repository: {self.art_repo}")

    async def add_art(self,
                      art_data: "ArtUploadSchema",
                      art_file: "UploadFile",
                      ) -> int:
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