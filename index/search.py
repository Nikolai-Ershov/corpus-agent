import math


def cos(vec1, vec2):
    scalar = sum(x * y for x, y in zip(vec1, vec2))

    vec1_length = math.sqrt(sum(i ** 2 for i in vec1))
    vec2_length = math.sqrt(sum(i ** 2 for i in vec2))

    vec_length = vec1_length * vec2_length
    result = scalar / vec_length

    return result


def search(query: str, chunks: list, k: int, embedder):
    query_vec = embedder.embed(query)

    result = []
    for inf in chunks:
        score = cos(query_vec, inf["vector"])

        chunks_dict = {
            "chunk_id": inf["chunk_id"],
            "origin_ref": inf["origin_ref"],
            "text": inf["text"],
            "score": float(score)
        }

        result.append(chunks_dict)

    sorted_result = sorted(result, key=lambda x: x["score"], reverse=True)[:k]

    return sorted_result
