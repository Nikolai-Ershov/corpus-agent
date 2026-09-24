import os
os.environ["HF_HUB_OFFLINE"] = "1"

from index.vector_store import VectorStore
from index.embed import Embedder
from index.chunk import chunk
from ingestion.plaintext import PlaintextAdapter

embedder = Embedder()
vector_store = VectorStore()
adapter = PlaintextAdapter()

records = adapter.parse("data/notes") + adapter.parse("data/base")


def run(path):

    for record in records:
        chunks = chunk(record.content)

        for chunk_text in chunks:
            vector = embedder.embed(chunk_text)
            vector_store.add(record.id, chunk_text, vector)

    vector_store.save(path)


if __name__ == "__main__":
    run("data/corpus_index.json")

