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
        logger.info("bucket Client initialized")
        try:
            self.bucket: Bucket = self.client.get_bucket(bucket_or_name=bucket_name)
        except GoogleCloudError as err:
            logger.critical(f"Error during connection to bucket. Error: {err}")
            raise err

    def upload_file(self,
                    file_obj: "BinaryIO",
                    blob_name: str,
                    ) -> str:
        """
        Upload a file to bucket and return the blob's name.

        :param file_obj: File object opened in binary mode.
        :param blob_name: Name of the blob in bucket.
        :return: Name of the uploaded blob.
        """
        logger.warning("Started uploading file into bucket")
        try:
            blob: "Blob" = self.bucket.blob(blob_name=blob_name)
            blob.upload_from_file(file_obj=file_obj, rewind=True)
            logger.debug(f"blob: {blob}")
            logger.info(f"Finished uploading file into bucket")
            return blob.name
        except GoogleCloudError as err:
            logger.error(f"Cloud error during uploading: {err}")
            raise err

    def delete_file(self, blob_name: str) -> None:
        """
        Delete a file from bucket by its blob name.

        :param blob_name: Name of the blob in bucket to delete.
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
        Generate a signed URL for a Google Cloud Storage blob.

        Args: blob_name (str), the name of the blob for which to generate the URL.
        Returns: String, the signed URL for accessing the blob.
        Raises: GoogleCloudError, if an error occurs during URL generation.
        """
        try:
            logger.warning(f"Started generating url, blob_name: {blob_name}")
            blob: Blob = self.bucket.blob(blob_name=blob_name)
            result_url: str = blob.generate_signed_url(
                version="v4", expiration=timedelta(days=settings.s3.expiration_days)
            )
            return result_url
        except GoogleCloudError as err:
            logger.error(f"Google Cloud error during URL generation: {err}")
            raise err
