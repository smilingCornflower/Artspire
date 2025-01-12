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

if TYPE_CHECKING:
    from typing import Self

S3_REQUEST = "S3_IMAGE_REQUEST"


# message body is json
#     {img_base64: string (base64 encoded file),
#      img_type: string
#      blob_name: string}

class S3RpcServer(RmqRpcServer):
    def __init__(self):
        super().__init__(queue_name=S3_REQUEST)

    async def msg_handler(self, message_body: str) -> str:
        result: dict = {"status": None, "img_name": None}
        try:
            img_data: dict = json.loads(message_body)
            img_base64: str = img_data["img_base64"]
            img_binary: bytes = base64.b64decode(img_base64)
            img_bytes_io: BytesIO = BytesIO(img_binary)

            img_jpg: BytesIO = await s3_service.convert_image_file_to_jpg(
                image_file=img_bytes_io, image_type=img_data["img_type"]
            )
            img_name: str = s3_service.upload_file(file_obj=img_jpg,
                                                   blob_name=img_data["blob_name"])
            result["status"] = settings.project_statuses.success
            result["img_name"] = img_name
        except json.decoder.JSONDecodeError as e:
            logger.critical(f"img_data decoding error: {e}")
            result["status"] = settings.project_statuses.json_decode_error
        except InvalidImageTypeHTTPException as e:
            logger.error(f"img_type is invalid {e}")
            result["status"] = settings.project_statuses.img_invalid_type_error
        except OSError as e:
            logger.error(f"OSError occurred: {e}")
            result["status"] = settings.project_statuses.os_error
        except GoogleCloudError as e:
            logger.error(f"GoogleCloudError occured: {e}")
            result["status"] = settings.project_statuses.google_cloud_error
        result_json: str = json.dumps(result)
        return result_json

    async def __aenter__(self) -> "Self":
        await self.connect()
        logger.info("S3RpcServer connected to RabbitMQ and queue declared successfully.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await s3_rpc_server.cleanup()
        if exc_type:
            logger.critical(f"Unexpected error occured: {e}")
            return False


async def _run_s3_rpc_server() -> None:
    s3_rpc_server = S3RpcServer()
    async with s3_rpc_server as server:
        await server.process_messages()


async def s3_server():
    s3_server_task: asyncio.Task | None = None
    try:
        while True:
            if s3_server_task is None or s3_server_task.done():
                s3_server_task = asyncio.create_task(_run_s3_rpc_server())

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