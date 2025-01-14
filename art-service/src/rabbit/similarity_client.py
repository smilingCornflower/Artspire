import json

from config import logger
from .rpc_client import run_rpc_client

SIMILARITY_REQUEST: str = "similarity_request"


async def run_similarity_client(art_id: int) -> list[int]:
    logger.warning(f"Started run_similarity_client with art_id: {art_id}")
    art_ids_json: str = await run_rpc_client(body=str(art_id), routing_key=SIMILARITY_REQUEST)
    art_ids: list[int] = json.loads(art_ids_json)
    return art_ids
