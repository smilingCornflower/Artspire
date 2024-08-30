from .rpc_client import run_rpc_client, RmqRpcClient
import json
from config import logger
from exceptions.http_exc import InternalServerErrorHTTPException

JWT_REQUEST: str = "jwt_request"


async def run_jwt_client(body: str) -> dict:
    json_result: str = await run_rpc_client(body=body, routing_key=JWT_REQUEST)
    try:
        result: dict = json.loads(json_result)
        return result
    except json.JSONDecodeError as err:
        logger.error(f"Error: {err}")
        raise InternalServerErrorHTTPException
