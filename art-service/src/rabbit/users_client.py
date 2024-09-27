from .rpc_client import run_rpc_client, RmqRpcClient
import json

USERS_REQUEST: str = "users_request"


async def run_users_client(users_id: list | set) -> list:
    users_id: list = list(users_id)
    users_id_json = json.dumps(users_id)
    users_info_json: str = await run_rpc_client(body=users_id_json, routing_key=USERS_REQUEST)
    users_info: list = json.loads(users_info_json)

    return users_info
