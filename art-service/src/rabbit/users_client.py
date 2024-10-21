from .rpc_client import run_rpc_client, RmqRpcClient
import json
from config import logger
from schemas.user import UserEntity

USERS_REQUEST: str = "users_request"


async def run_users_client(users_id: list) -> dict[int, "UserEntity"]:
    """
    Sends a request to the RabbitMQ queue to retrieve user information based on a list of user IDs.

    This function sends a JSON-encoded list of `user_id` values to the `users_request` queue via RabbitMQ.
    The authorization service processes the request and returns a JSON-encoded response, where each key is a
    user ID and each value is a dictionary containing user information such as `id`, `username`, `email`, etc.

    The function validates the received data and creates `UserEntity` models for each user. It returns a
    dictionary where the keys are user IDs, and the values are instances of `UserEntity`.

    If the input list contains duplicate user IDs (e.g., `[1, 1, 7]`), the result will only contain unique
    user IDs (e.g., `{1: user_1, 7: user_7}`).

    :param users_id: A list of user IDs for which information needs to be retrieved.
    :return: A dictionary where the keys are user IDs, and the values are `UserEntity` instances with the user's information.
    :raises ValidationError: If the data from the service does not match the expected structure.
    """
    logger.warning(f"Started run_users_client with users_id: {users_id}")
    users_id_json = json.dumps(users_id)
    users_info_json: str = await run_rpc_client(body=users_id_json, routing_key=USERS_REQUEST)
    users_info: list[dict] = json.loads(users_info_json)

    user_entities_dict: dict[int, "UserEntity"] = {
        user["id"]: UserEntity.model_validate(user) for user in users_info
    }

    return user_entities_dict
