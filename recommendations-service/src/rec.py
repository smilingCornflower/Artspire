import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix, load_npz
from config import settings, logger
import pickle
from red import r
from exceptions import ArtNotFoundException


def update_similarity_arts_matrix():
    matrix: csr_matrix = load_npz(settings.paths.arts_csr)
    similarity_matrix: np.ndarray = cosine_similarity(matrix)
    np.save(settings.paths.arts_sim_matrix, similarity_matrix)


def get_similar_arts(art_id: int):
    redis_key_name = f"similar_arts_for_{art_id}"
    art_ids = r.lrange(redis_key_name, 0, -1)
    if art_ids:
        return [int(i) for i in art_ids]
    with open(settings.paths.art_ids_to_indices, "rb") as file:
        art_ids_to_indices: dict = pickle.load(file)
    with open(settings.paths.art_indices_to_ids, "rb") as file:
        art_indices_to_ids: dict = pickle.load(file)
    if art_id not in art_ids_to_indices:
        raise ArtNotFoundException(art_id)
    similarity_matrix: np.ndarray = np.load(settings.paths.arts_sim_matrix)
    art_index = art_ids_to_indices[art_id]

    similar_art_indices: np.ndarray = similarity_matrix[art_index]
    similar_art_indices = np.argsort(-similar_art_indices)
    result = [int(art_indices_to_ids[i]) for i in similar_art_indices]
    if art_id in result:
        result.remove(art_id)

    r.rpush(redis_key_name, *result)
    r.expire(redis_key_name, settings.redis_ex.art_ids)
    return result
