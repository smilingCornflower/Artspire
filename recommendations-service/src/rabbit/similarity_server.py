import asyncio
from .rpc_server import RmqRpcServer
import json
import pickle
from config import logger, settings
from rec import get_similar_arts
from exceptions import ArtNotFoundException

SIMILARITY_REQUEST: str = "similarity_request"


class SimilarityRpcServer(RmqRpcServer):
    def __init__(self):
        super().__init__(queue_name=SIMILARITY_REQUEST)

    async def msg_handler(self, message_body: str) -> str:
        try:
            art_id: int = int(message_body)
            similar_art_ids: list[int] = get_similar_arts(art_id)
            response: str = json.dumps(similar_art_ids)
            return response
        except ArtNotFoundException as e:
            logger.error(f"Expected Exception: {e}")
            logger.info("Returning alternative output")
            with open(settings.paths.art_ids_to_indices, "rb") as file:
                art_ids_to_indices: dict = pickle.load(file)
            art_ids: list[int] = [int(i) for i in art_ids_to_indices]
            response: str = json.dumps(art_ids)
            return response


async def _run_similarity_rpc_server() -> None:
    similarity_rpc_server = SimilarityRpcServer()
    try:
        await similarity_rpc_server.connect()
        logger.info("SimilarityRpcServer connected to RabbitMQ and queue declared successfully.")
        await similarity_rpc_server.process_messages()
    except Exception as err:
        logger.critical(f"Exception: {err}", exc_info=True)
        await similarity_rpc_server.cleanup()
        raise err


async def similarity_server():
    similarity_server_task: asyncio.Task | None = None
    try:
        while True:
            if similarity_server_task is None or similarity_server_task.done():
                similarity_server_task = asyncio.create_task(_run_similarity_rpc_server())
            try:
                await similarity_server_task
            except asyncio.CancelledError:
                logger.info("Similarity server task was cancelled.")
                break
            except Exception as e:
                logger.critical(f"Similarity server task encountered an error: {e}", exc_info=True)
                logger.info("Restarting Similarity server task...")
    finally:
        if similarity_server_task:
            similarity_server_task.cancel()
        try:
            await similarity_server_task
            logger.critical("Similarity server not cancelled")
        except asyncio.CancelledError:
            logger.info("Similarity server task was cancelled.")
