from .rpc_server import RmqRpcServer
from fastapi import UploadFile

from bucket.s3_service import s3_service
from config import settings, logger
from io import BytesIO
from exceptions.http_exc import InvalidImageTypeHTTPException
from google.cloud.exceptions import GoogleCloudError
import base64
import json
import asyncio
from typing import TYPE_CHECKING
from schemas.rabbit_ import S3AddSchema, S3AddResponse, S3GetSchema, S3GetResponse
from pydantic import ValidationError

if TYPE_CHECKING:
    from typing import Self

S3_ADD_REQUEST = "s3_image_add_request"
S3_GET_REQUEST = "s3_image_get_request"


class S3RpcAddServer(RmqRpcServer):
    def __init__(self):
        super().__init__(queue_name=S3_ADD_REQUEST)

    async def msg_handler(self, message_body: str) -> str:
        """
        Decodes the incoming JSON message (containing base64 image data, image type, and blob name),
        converts the image to JPEG, and uploads it to an external storage.

        Steps:
          1. Parse `message_body` into a :class:`S3AddSchema`.
          2. Decode the base64 string into binary data.
          3. Convert the binary image to JPEG format if needed.
          4. Upload the resulting image to a storage bucket.
          5. Prepare and return a JSON-encoded :class:`S3AddResponse`.

        :param message_body: JSON string that includes the base64-encoded image data and metadata.
        :type message_body: str
        :return: JSON string of the :class:`S3AddResponse` schema, containing status and blob name.
        :rtype: str
        :raises ValidationError: If the input JSON fails schema validation.
        :raises GoogleCloudError: If an error occurs during upload to a Google Cloud storage bucket.
        :raises InvalidImageTypeHTTPException: If the provided image type is not supported.
        :raises OSError: If any file I/O or image conversion error occurs.
        """
        result = S3AddResponse()
        try:
            img_data = S3AddSchema.model_validate_json(message_body)
            logger.debug("message_body validated")

            img_base64: str = img_data.img_base64
            img_binary: bytes = base64.b64decode(img_base64)
            img_bytes_io: BytesIO = BytesIO(img_binary)

            img_jpg: BytesIO = await s3_service.convert_image_file_to_jpg(
                image_file=img_bytes_io, image_type=img_data.img_type)
            logger.debug("image converted to jpg")

            blob_name: str = s3_service.upload_file(file_obj=img_jpg, blob_name=img_data.blob_name)
            result.status = settings.project_statuses.success
            result.blob_name = blob_name
        except (ValidationError, GoogleCloudError, InvalidImageTypeHTTPException, OSError) as e:
            logger.critical(e, exc_info=True)
            if type(e) is ValidationError:
                result.status = settings.project_statuses.validation_error
            elif type(e) is GoogleCloudError:
                result.status = settings.project_statuses.google_cloud_error
            elif type(e) is InvalidImageTypeHTTPException:
                result.status = settings.project_statuses.img_invalid_type_error
            else:
                result.status = settings.project_statuses.os_error
        result_json: str = result.model_dump_json()
        logger.debug(f"result_json = {result_json}")
        return result_json


class S3RpcGetServer(RmqRpcServer):
    """
    An RPC server that listens for image retrieval requests via RabbitMQ, constructs
    the image URL from the specified blob name, and returns the result.

    Inherits from :class:`RmqRpcServer` to leverage standard RabbitMQ connection and
    message-handling patterns.
    """
    def __init__(self):
        super().__init__(queue_name=S3_GET_REQUEST)

    async def msg_handler(self, message_body: str) -> str:
        """
        Processes incoming messages that request an image URL.

        Steps:
          1. Parses the message JSON into :class:`S3GetSchema`.
          2. Uses `s3_service.create_url(...)` to generate a public or signed URL for the given blob_name.
          3. Builds and returns an :class:`S3GetResponse` with the resulting URL.

        :param message_body: str — A JSON-encoded string containing the `blob_name` field.
        :return: str — A JSON-encoded :class:`S3GetResponse` with the status and `img_url`.
        """
        result = S3GetResponse()
        img_blob_name = S3GetSchema.model_validate_json(message_body).blob_name
        logger.info(f"img_blob_name = {img_blob_name}")
        img_url: str = s3_service.create_url(blob_name=img_blob_name)

        result.status = settings.project_statuses.success
        result.img_url = img_url
        result_json: str = result.model_dump_json()
        logger.info(f"result_json = {result_json}")
        return result_json


async def _run_s3_rpc_add_server() -> None:
    logger.info(f"_run_s3_rpc_add_server")
    s3_rpc_add_server = S3RpcAddServer()
    async with s3_rpc_add_server as server:
        await server.process_messages()


async def _run_s3_rpc_get_server() -> None:
    logger.info(f"_run_s3_rpc_get_server")
    s3_rpc_get_server = S3RpcGetServer()
    async with s3_rpc_get_server as server:
        await server.process_messages()


async def s3_server(_run_server: callable):
    """
    Continuously runs a server task, restarting it upon errors.

    :param _run_server: Coroutine to start the server.
    """
    s3_server_task: asyncio.Task | None = None
    try:
        while True:
            if s3_server_task is None or s3_server_task.done():
                s3_server_task = asyncio.create_task(_run_server())
            try:
                await s3_server_task
            except asyncio.CancelledError:
                logger.info("S3 server task was cancelled.")
                break
            except Exception as e:
                logger.error(f"S3 server task encountered an error: {e}", exc_info=True)
                logger.info("Restarting S3 server task...")
            await asyncio.sleep(1)
    finally:
        if s3_server_task:
            s3_server_task.cancel()
            try:
                await s3_server_task
                logger.critical("S3 server task not cancelled")
            except asyncio.CancelledError:
                logger.info("S3 server task was cancelled successfully.")


async def s3_add_server():
    await s3_server(_run_server=_run_s3_rpc_add_server)


async def s3_get_server():
    await s3_server(_run_server=_run_s3_rpc_get_server)
