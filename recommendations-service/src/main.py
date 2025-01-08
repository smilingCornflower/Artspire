import asyncio
import redis

import numpy as np
from scipy.sparse import load_npz, csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from utils.data_processor import update_arts_matrix
from rec import get_similar_arts, update_similarity_arts_matrix
from config import settings, logger
from rabbit.similarity_server import similarity_server
from contextlib import asynccontextmanager


@asynccontextmanager
async def similarity_lifespan():
    similarity_task = asyncio.create_task(similarity_server())
    try:
        yield
    finally:
        similarity_task.cancel()
        await asyncio.gather(similarity_task, return_exceptions=True)


async def main():
    async with similarity_lifespan():
        while True:
            await asyncio.sleep(1)  # Замените на вашу логику


if __name__ == "__main__":
    asyncio.run(main())
