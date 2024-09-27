from .rpc_server import RmqRpcServer
import json
from api.dependencies._get_user_service import get_user_service
from services.users import UserService
from aio_pika.exceptions import AMQPException
import asyncio
from config import logger

USERS_REQUEST: str = "users_request"

# to_receive: users_id a list of int


class UsersRpcServer(RmqRpcServer):
    def __init__(self):
        super().__init__(queue_name=USERS_REQUEST)

    async def msg_handler(self,
                          message_body: str,
                          users_service: "UserService" = get_user_service()
                          ) -> str:
        users_id: list[int] = json.loads(message_body)
        result_users: list = await users_service.get_all_users(users_id=users_id)
        users_json: str = json.dumps(result_users)

        return users_json


async def _run_users_rpc_server() -> None:
    users_rpc_server: UsersRpcServer = UsersRpcServer()
    try:
        await users_rpc_server.connect()
        logger.info("UsersRpcServer connected to RabbitMQ and queue declared successfully.")
        await users_rpc_server.process_messages()
    except (AMQPException, Exception) as err:
        logger.error(f"error: {err}")
        await users_rpc_server.cleanup()


async def users_server():
    users_server_task: "asyncio.Task | None" = None
    try:
        while True:
            if users_server_task is None or users_server_task.done():
                users_server_task = asyncio.create_task(_run_users_rpc_server())

            try:
                await users_server_task
            except asyncio.CancelledError:
                logger.info("Users server task was cancelled.")
                break
            except Exception as e:
                logger.error(f"Users server task encountered an error: {e}", exc_info=True)
                logger.info("Restarting Users server task...")

            await asyncio.sleep(1)
    finally:
        if users_server_task:
            users_server_task.cancel()
            try:
                await users_server_task
                logger.critical("Users server not cancelled")
            except asyncio.CancelledError:
                logger.info("Users server task was cancelled.")
