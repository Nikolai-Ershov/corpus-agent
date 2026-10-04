from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-m3")
        self.model.max_seq_length = 512

    def embed(self, text: str):
        return self.model.encode(text)
