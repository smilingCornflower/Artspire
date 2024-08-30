# Standard libraries
from datetime import datetime, timezone
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
from exceptions.http_exc import FailedUploadHttpException
from config import logger

if TYPE_CHECKING:
    from repositories.arts import ArtRepository
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
        return new_art_id