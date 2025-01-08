import asyncio
import redis

import numpy as np
from scipy.sparse import load_npz, csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from utils.data_processor import update_arts_matrix
from rec import get_similar_arts, update_similarity_arts_matrix
from config import settings


async def main():
    print(get_similar_arts(14))


if __name__ == "__main__":
    asyncio.run(main())
