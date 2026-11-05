"""Build the vector index: parse every record in the corpus, chunk it,
embed each chunk, and save the result as JSON."""


import os

# must come before the Embedder import below, which wraps SentenceTransformer
# and pulls in huggingface_hub transitively
os.environ["HF_HUB_OFFLINE"] = "1"

from index.vector_store import VectorStore
from index.embed import Embedder
from index.chunk import chunk
from ingestion.plaintext import PlaintextAdapter


# one-off script, never imported as a module — module-level setup here is fine
embedder = Embedder()
vector_store = VectorStore()
adapter = PlaintextAdapter()

# both collections go into one flat list of Record objects — the whole
# corpus gets indexed together; origin_ref is the only thing that still
# tells notes and transcripts apart afterward
records = adapter.parse("data/notes") + adapter.parse("data/base")


def run(path):
    for record in records:  # one record (document/note) at a time
        chunks = chunk(record.content)  # split that record's own text into chunks

        for chunk_text in chunks:  # embed each chunk individually
            vector = embedder.embed(chunk_text)
            # a new stored entry (origin_ref, text, vector) — nothing is
            # mutated on chunk_text itself
            vector_store.add(record.origin_ref, chunk_text, vector)

    vector_store.save(path)


if __name__ == "__main__":
    run("data/corpus_index.json")