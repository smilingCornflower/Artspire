from .rpc_client import run_rpc_client
from fastapi import UploadFile
import base64
import json
from config import logger, settings
from typing import BinaryIO
from exceptions.http import InternalServerHTTPException, InvalidImageTypeHTTPException
from schemas.rabbit_ import S3AddSchema, S3AddResponse, S3GetSchema, S3GetResponse
from pydantic import ValidationError


S3_ADD_REQUEST: str = "s3_image_add_request"
S3_GET_REQUEST: str = "s3_image_get_request"


async def run_s3_add_client(body: S3AddSchema) -> str:
    """
    Sends an image-related request via RabbitMQ and returns the blob name if successful.

    :param body: Pydantic schema with base64 image data, image type, and blob name.
    :return: Blob name in the external storage.
    :raises InterServerHTTPException: If the response status is not 1000.
    :raises InvalidImageTypeHTTPException: If the response status is 1002
    Note: Correct image types are .jpg .png .webp
    """
    json_result: str = await run_rpc_client(body=body.model_dump_json(), routing_key=S3_ADD_REQUEST)
    result = S3AddResponse.model_validate_json(json_result)
    logger.debug(f"result = {result}")
    if result.status == settings.rpc_status_success:
        return result.blob_name
    elif result.status == settings.rpc_status_img_invalid_type_error:
        raise InvalidImageTypeHTTPException
    else:
        logger.critical(f"result's status = {result.status}")
        raise InternalServerHTTPException


async def run_s3_get_client(body: S3GetSchema) -> str:
    """
    Sends an RPC request to retrieve an image URL for a given blob name.

    :param body: S3GetSchema — A Pydantic schema containing the blob_name for which an image URL is requested.
    :return: str — The URL of the requested image.
    :raises InternalServerHTTPException: If the remote server indicates a failure (non-success status).
    """
    json_result: str = await run_rpc_client(body=body.model_dump_json(),
                                            routing_key=S3_GET_REQUEST)
    logger.debug(f"type(json_result) = {type(json_result)}")
    result = S3GetResponse.model_validate_json(json_result)

    if result.status == settings.rpc_status_success:
        return result.img_url
    else:
        logger.critical(f"result's status = {result.status}")
        raise InternalServerHTTPException
