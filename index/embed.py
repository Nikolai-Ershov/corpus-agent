"""Wraps the embedding model: bge-m3, one call → one fixed-size vector."""

from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-m3")
        # explicit, not left to the library's default — current 150-word
        # chunks never get close to this; it's a safety ceiling in case
        # something much longer ever gets passed to embed() by mistake.
        # Anything past 512 tokens gets silently truncated, not rejected.
        self.model.max_seq_length = 512

    def embed(self, text: str):
        return self.model.encode(text)
