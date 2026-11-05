"""Vector search over the corpus index using cosine similarity."""


import numpy as np


def cos(query_vec, matrix):
    """Cosine similarity between one query vector and every row (chunk)
    in `matrix` at once — vectorized so it scores all chunks in a single
    matrix multiply instead of looping per chunk."""

    scalar = matrix @ query_vec

    query_length = np.linalg.norm(query_vec)
    matrix_lengths = np.linalg.norm(matrix, axis=1)

    result = scalar / (matrix_lengths * query_length)
    return result


def search(query: str, chunks: list, k: int, embedder):
    """Embed the query, score it against every chunk, return the top k
    matches sorted by score (highest first)."""

    query_vec = embedder.embed(query)

    vectors = [inf["vector"] for inf in chunks]
    matrix = np.asarray(vectors)  # cos() needs a numpy array to do the matrix multiply

    scores = cos(query_vec, matrix)

    # argsort gives ascending order; take the last k (highest scores),
    # then reverse so index 0 is the best match
    top_k_indices = np.argsort(scores)[-k:][::-1]

    result = []
    for i in top_k_indices:
        i = int(i)  # numpy.int64 → plain int, so it indexes chunks[] cleanly
        result.append({
            "chunk_id": chunks[i]["chunk_id"],
            "origin_ref": chunks[i]["origin_ref"],
            "text": chunks[i]["text"],
            "score": float(scores[i]),
        })

    return result
