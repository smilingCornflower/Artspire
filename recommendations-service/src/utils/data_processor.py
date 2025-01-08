# Standard library imports
from pathlib import Path
import joblib
import pickle

# Third-party imports
import numpy as np
from scipy.sparse import csr_matrix, hstack, save_npz, vstack
from scipy.spatial.distance import cosine
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from compress_fasttext.models import CompressedFastTextKeyedVectors

# Local application imports
from config import logger, settings
from database.arts import ArtsService


def to_binary_vector(number: int, arr_len: int = 16) -> np.ndarray:
    binary_lst = list(bin(number)[2:].zfill(arr_len))
    return np.array(binary_lst, dtype=np.int8)


async def _get_csr_matrix_of_vectorized_tags(tag_ids: list[list[int]]) -> csr_matrix:
    logger.info(f"STARTED len(tag_ids) = {len(tag_ids)}")
    vector_size = 100
    cft_model = CompressedFastTextKeyedVectors.load(str(settings.paths.cft_model))
    pca_model: PCA = joblib.load(str(settings.paths.pca_model))
    logger.debug(f"cft_model and pca_model are initialized")

    tag_ids = [tags[:settings.arts.max_tags] for tags in tag_ids]

    arts_service = ArtsService()
    all_tags: list[tuple[int, str]] = await arts_service.get_all_tags()
    all_tags_mapping: dict[int, str] = {i[0]: i[1] for i in all_tags}
    logger.debug(f"len(all_tags_mapping) = {len(all_tags_mapping)}")

    tags_vectors_csr_matrices: list[csr_matrix] = []
    for row in tag_ids:
        tags_matrix = np.zeros((settings.arts.max_tags, vector_size), dtype=np.float32)
        tags_vectors = np.array([cft_model.get_vector(all_tags_mapping[tag_id]) for tag_id in row])
        for i, vec in enumerate(tags_vectors):
            # cft_model.get_vector() returns a vector with 300 dimensions, while we need 100D.
            transformed_vector: np.ndarray = pca_model.transform(vec.reshape(1, -1))[0]
            tags_matrix[i] = transformed_vector
        tags_csr_matrix = csr_matrix(tags_matrix.reshape(-1))
        tags_vectors_csr_matrices.append(tags_csr_matrix)

    tags_vectors_csr_matrix: csr_matrix = vstack(tags_vectors_csr_matrices)
    return tags_vectors_csr_matrix


#     arts_data_csr: csr_matrix = hstack(
#         [user_ids_vec, likes_scaled_csr, views_scaled_csr, tags_csr_matrix])


async def update_arts_matrix():
    logger.warning("STARTED")
    arts_service = ArtsService()
    arts_data: list[list] = await arts_service.get_new_arts_data()

    art_ids, user_ids, like_counts, view_counts = map(np.array, zip(*[i[:4] for i in arts_data]))

    user_id_binary_vectors = np.array([to_binary_vector(i) for i in user_ids])

    likes_scaler, views_scaler = MinMaxScaler(), MinMaxScaler()
    like_counts_scaled = likes_scaler.fit_transform(like_counts.reshape(-1, 1))
    view_counts_scaled = views_scaler.fit_transform(view_counts.reshape(-1, 1))
    logger.debug(f" like_counts_scaled.shape = {like_counts_scaled.shape}")

    tags_ids: list[list[int]] = [i[4] for i in arts_data]
    tags_csr_matrix = await _get_csr_matrix_of_vectorized_tags(tags_ids)
    logger.debug(f"tags_csr_matrix.shape = {tags_csr_matrix.shape}")

    user_ids_csr = csr_matrix(user_id_binary_vectors)
    like_counts_scaled_csr = csr_matrix(like_counts_scaled)
    view_counts_scaled_csr = csr_matrix(view_counts_scaled)

    arts_data_csr: csr_matrix = hstack(
        [user_ids_csr, like_counts_scaled_csr, view_counts_scaled_csr, tags_csr_matrix]
    )
    logger.info(f"arts_data_csr.shape = {arts_data_csr.shape}")
    save_npz(settings.paths.arts_csr, arts_data_csr)

    art_indices_to_ids: dict = {i: val for i, val in enumerate(art_ids)}
    art_ids_to_indices: dict = {val: i for i, val in enumerate(art_ids)}

    with open(settings.paths.art_indices_to_ids, "wb") as file:
        pickle.dump(art_indices_to_ids, file)
    with open(settings.paths.art_ids_to_indices, "wb") as file:
        pickle.dump(art_ids_to_indices, file)
