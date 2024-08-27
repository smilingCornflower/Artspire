import os
from typing import TYPE_CHECKING

from google.cloud.exceptions import GoogleCloudError
from google.cloud.storage import Client

from config import settings, logger
from datetime import timedelta
if TYPE_CHECKING:
    from google.cloud.storage.bucket import Bucket
    from google.cloud.storage.blob import Blob
    from typing import BinaryIO

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(settings.s3.credentials_path)


class S3Client:
    def __init__(self,
                 bucket_name: str,
                 ):
        self.client: Client = Client()
        logger.info("S3 Client initialized")
        try:
            self.bucket: Bucket = self.client.get_bucket(bucket_or_name=bucket_name)
        except GoogleCloudError as err:
            logger.critical(f"Error during connection to bucket. Error: {err}")
            raise err

    def upload_file(self,
                    file_obj: "BinaryIO",
                    blob_name: str) -> str:
        """
        Upload a file to S3 and return the blob's name.

        :param file_obj: File object opened in binary mode.
        :param blob_name: Name of the blob in S3.
        :return: Name of the uploaded blob.
        """
        logger.warning("Started uploading file into S3")
        try:
            blob: "Blob" = self.bucket.blob(blob_name=blob_name)
            blob.upload_from_file(file_obj=file_obj, rewind=True)
            logger.debug(f"blob: {blob}")
            logger.info(f"Finished uploading file into S3")
            return blob.name
        except GoogleCloudError as err:
            logger.error(f"Cloud error during uploading: {err}")
            raise err

    def delete_file(self, blob_name: str) -> None:
        """
        Delete a file from S3 by its blob name.

        :param blob_name: Name of the blob in S3 to delete.
        """
        try:
            logger.warning(f"Started deleting blob: {blob_name}")
            blob: Blob = self.bucket.blob(blob_name=blob_name)
            blob.delete()
            logger.info(f"Finished deleting blob")
        except GoogleCloudError as err:
            logger.error(f"Cloud error during deletion: {err}")
            raise err

    def create_url(self, blob_name: str) -> str:
        """

        """
        try:
            logger.warning(f"Started generating url, blob_name: {blob_name}")
            blob: Blob = self.bucket.blob(blob_name=blob_name)
            result_url: str = blob.generate_signed_url(version="v4", expiration=timedelta(days=settings.s3.expiration_days))
            logger.info(f"Finished generating url, result_url: {result_url}")
            return result_url

        except GoogleCloudError as err:
            logger.error(f"Google Cloud error during URL generation: {err}")
            raise err

s3_client = S3Client(
    bucket_name=settings.s3.bucket_name
)
