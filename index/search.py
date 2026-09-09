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
        res = (inf["text"], cos(query_vec, inf["vector"]))
        result.append(res)

    sorted_result = sorted(result, key=lambda x: x[1], reverse=True)[:k]

    return sorted_result












