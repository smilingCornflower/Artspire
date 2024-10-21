from .s3_client import S3Client
from fastapi import UploadFile
from exceptions.http_exc import (
    InvalidImageTypeHTTPException,
    InternalServerErrorHTTPException,
)
import io
from typing import TYPE_CHECKING
from google.cloud.exceptions import GoogleCloudError
from config import logger, settings
from typing import BinaryIO, TYPE_CHECKING
import shortuuid
from PIL import Image

if TYPE_CHECKING:
    from PIL import ImageFile, Image
    from io import BytesIO


class S3Service(S3Client):
    IMG_TYPES: tuple[str] = ("image/jpeg", "image/png", "image/webp")
    JPEG: str = "image/jpeg"

    async def _convert_to_jpg(self, image: "UploadFile") -> "BytesIO":
        """
        Converts the uploaded image to JPEG format if the image type is valid.
        Supported image types are JPEG, PNG, and WEBP. If the image has an alpha channel (RGBA),
        it will be converted to RGB for proper saving in JPEG format.

        Parameters:
        ----------
        image : UploadFile
            The uploaded image file to be processed.

        Returns:
        ----------
        BytesIO
            A BytesIO object containing the image in JPEG format.

        Raises:
        ----------
        InvalidImageTypeHTTPException
            If the uploaded image type is not one of the supported types.
        OSError
            If an error occurs during the opening or processing of the image (e.g., if the image is corrupted).
        """
        logger.info("STARTED _convert_to_jpg()")
        image_type: str = image.content_type
        if image_type not in self.IMG_TYPES:
            exception_text: str = f"Invalid image type: {image_type}. Expected one of: {', '.join(self.IMG_TYPES)}"
            raise InvalidImageTypeHTTPException(detail=exception_text)

        # type(image_file) --> SpooledTemporaryFile
        image_file: "BinaryIO" = image.file

        try:
            image: "ImageFile" = Image.open(image_file)
            if image.mode == 'RGBA':
                image: "Image" = image.convert('RGB')

            output: "BytesIO" = io.BytesIO()
            image.save(output, format="JPEG")
            output.seek(0)
            return output

        except OSError as err:
            logger.critical("OSError occurred during image processing: %s", err)
            raise err

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

        image_jpg = await self._convert_to_jpg(image=image_file)

        image_name: str = f"arts/{user_id}/{shortuuid.uuid()}.jpg"
        try:
            blob_name: str = self.upload_file(file_obj=image_jpg, blob_name=image_name)
            logger.info(f"FINISHED upload_image()")
        except GoogleCloudError as err:
            logger.error(f"Error: {err}")
            raise InternalServerErrorHTTPException

        return blob_name


s3_service: S3Service = S3Service(
    bucket_name=settings.s3.bucket_name
)
