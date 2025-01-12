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

    async def convert_image_file_to_jpg(self, image_file: BinaryIO, image_type: str) -> "BytesIO":
        """
       Converts a binary image file to JPEG format if the image type is valid.
       Supported image types are JPEG, PNG, and WEBP. Converts images with an alpha channel (RGBA) to RGB.

       Parameters:
       ----------
       image_file : BinaryIO
           The binary image file to be processed.
       image_type : str
           The MIME type of the image file.

       Returns:
       ----------
       BytesIO
           A BytesIO object containing the image in JPEG format.

       Raises:
       ----------
       InvalidImageTypeHTTPException
           If the image type is not one of the supported types.
       OSError
           If an error occurs during the opening or processing of the image.
       """
        logger.debug(f"type(image_file) = {type(image_file)}")
        logger.debug(f"isinstance(image_file, BinaryIO) = {isinstance(image_file, BinaryIO)}")

        if image_type not in self.IMG_TYPES:
            exception_text: str = f"Invalid image type: {image_type}. Expected one of: {', '.join(self.IMG_TYPES)}"
            raise InvalidImageTypeHTTPException(detail=exception_text)
        try:
            image: "ImageFile" = Image.open(image_file)
            if image.mode != 'RGB':
                image: "Image" = image.convert('RGB')

            output: "BytesIO" = io.BytesIO()
            image.save(output, format="JPEG")
            output.seek(0)
            return output
        except OSError as err:
            logger.critical("OSError occurred during image processing: %s", err)
            raise err

    async def _convert_upload_file_to_jpg(self, image: "UploadFile") -> "BytesIO":
        """
        Converts an uploaded image to JPEG format by validating and processing it.
        Supported image types are JPEG, PNG, and WEBP. Converts images with an alpha channel (RGBA) to RGB.

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
            If an error occurs during the opening or processing of the image.
        """
        logger.info("STARTED _convert_upload_file_to_jpg()")
        image_type: str = image.content_type

        # type(image_file) --> SpooledTemporaryFile
        image_file: "BinaryIO" = image.file
        jpg_img: "BytesIO" = await self.convert_image_file_to_jpg(image_file=image_file,
                                                                  image_type=image_type)
        return jpg_img

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

        image_jpg = await self._convert_upload_file_to_jpg(image=image_file)

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
