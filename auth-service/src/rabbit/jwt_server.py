import asyncio

from .rpc_server import RmqRpcServer
from utils.jwt_utils import decode_jwt, ACCESS_TOKEN_TYPE
from jwt.exceptions import PyJWTError
from aio_pika.exceptions import AMQPException
import json
from config import logger

JWT_REQUEST: str = "jwt_request"


# jwt_request: str = Just token itself
# jwt_response: str = Json string of format {"is_valid": bool, "decoded": dict | None}

class JwtRpcServer(RmqRpcServer):
    def __init__(self):
        super().__init__(queue_name=JWT_REQUEST)

    async def msg_handler(self, message_body: str) -> str:
        try:
            logger.debug(f"Decoding JWT: {message_body}")
            decoded: dict = decode_jwt(message_body)
            if decoded["type"] != ACCESS_TOKEN_TYPE:
                raise ValueError(f"Incorrect token type, expected: {ACCESS_TOKEN_TYPE} received: {decoded['type']}")
            response: dict = {
                "is_valid": True,
                "decoded": decoded,
            }
            logger.info(f"JWT decoded successfully: {decoded}")
        except (PyJWTError, ValueError) as err:
            logger.error(f"JWT decoding failed: {err}", exc_info=True)
            response: dict = {
                "is_valid": False,
                "decoded": None,
            }
        response_str: str = json.dumps(response)
        return response_str


async def _run_jwt_rpc_server() -> None:
    jwt_rpc_server: "JwtRpcServer" = JwtRpcServer()
    try:
        await jwt_rpc_server.connect()
        logger.info("JwtRpcServer connected to RabbitMQ and queue declared successfully.")
        await jwt_rpc_server.process_messages()
    except (AMQPException, PyJWTError, Exception) as err:
        logger.error(f"error: {err}")
        await jwt_rpc_server.cleanup()


async def jwt_server():
    jwt_server_task: "asyncio.Task | None" = None
    try:
        while True:
            if jwt_server_task is None or jwt_server_task.done():
                jwt_server_task = asyncio.create_task(_run_jwt_rpc_server())

            try:
                await jwt_server_task
            except asyncio.CancelledError:
                logger.info("JWT server task was cancelled.")
                break
            except Exception as e:
                logger.error(f"JWT server task encountered an error: {e}", exc_info=True)
                logger.info("Restarting JWT server task...")

            await asyncio.sleep(1)
    finally:
        if jwt_server_task:
            jwt_server_task.cancel()
            try:
                await jwt_server_task
                logger.critical("JWT server not cancelled")
            except asyncio.CancelledError:
                logger.info("JWT server task was cancelled.")
