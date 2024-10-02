from .s3_client import S3Client
from fastapi import UploadFile
from exceptions.http_exc import (
    InvalidImageTypeHTTPException,
    InternalServerErrorHTTPException,
)
from typing import TYPE_CHECKING
from google.cloud.exceptions import GoogleCloudError
from utils.img import convert_to_jpg
from config import logger, settings
import shortuuid

if TYPE_CHECKING:
    from typing import BinaryIO


class S3Service(S3Client):
    IMG_TYPES: tuple[str] = ("image/jpeg", "image/png", "image/webp")
    JPEG: str = "image/jpeg"

    async def upload_image(self, image_file: UploadFile, user_id: int) -> str:
        """
        Uploads an image file to S3 storage.

        This method handles the upload of an image to S3. If the file type is not one of the supported
        image formats (`image/jpeg`, `image/png`, `image/webp`), an `InvalidImageTypeHTTPException`
        is raised. If the image is not in JPEG format, it is converted to JPEG before upload.

        The `blob_name` for the image is automatically generated in the format `arts/{user_id}/{uuid}.jpg`.

        :param image_file: The image file to be uploaded.
        :param user_id: The ID of the user uploading the image.
        :return: The `blob_name` of the uploaded image.
        :raises InvalidImageTypeHTTPException: If the image file type is not supported.
        :raises InternalServerErrorHTTPException: If there is an error during the upload to S3.
        """
        logger.warning(f"Started upload_image()")

        image_type: str = image_file.content_type
        if image_type not in self.IMG_TYPES:
            exception_text: str = f"Invalid image type: {image_type}. Expected one of: {', '.join(self.IMG_TYPES)}"
            raise InvalidImageTypeHTTPException(detail=exception_text)

        image_file: BinaryIO = image_file.file
        if image_type != self.JPEG:
            logger.info(f"await convert_to_jpg(); image_type: {image_type}")
            image_file = await convert_to_jpg(image_file)

        image_name: str = f"arts/{user_id}/{shortuuid.uuid()}.jpg"
        try:
            blob_name: str = self.upload_file(file_obj=image_file, blob_name=image_name)
            logger.info(f"FINISHED upload_image()")
        except GoogleCloudError as err:
            logger.error(f"Error: {err}")
            raise InternalServerErrorHTTPException

        return blob_name


s3_service: S3Service = S3Service(
    bucket_name=settings.s3.bucket_name
)
