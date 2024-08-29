from .rpc_server import RmqRpcServer
from utils.jwt_utils import decode_jwt
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
            response: dict = {
                "is_valid": True,
                "decoded": decoded,
            }
            logger.info(f"JWT decoded successfully: {decoded}")
        except PyJWTError as err:
            logger.error(f"JWT decoding failed: {err}", exc_info=True)
            response: dict = {
                "is_valid": False,
                "decoded": None,
            }
        response_str: str = json.dumps(response)
        return response_str


async def run_jwt_server() -> None:
    jwt_server = JwtRpcServer()
    try:
        await jwt_server.connect()
        await jwt_server.process_messages()
    except AMQPException as err:
        logger.critical(f"AMQP error: {err}", exc_info=True)
        await jwt_server.cleanup()
    except PyJWTError as err:
        logger.error(f"JWT error: {err}", exc_info=True)
        await jwt_server.cleanup()
    except Exception as err:
        logger.error(f"Unexpected error: {err}", exc_info=True)
        await jwt_server.cleanup()
