import json
import uuid
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        self.chunks = []

    def add(self, origin_ref, text, vector):

        chunk_data = {
            "chunk_id": str(uuid.uuid4()),
            "origin_ref": origin_ref,
            "text": text,
            "vector": vector.tolist()
        }

        self.chunks.append(chunk_data)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.chunks, file, ensure_ascii=False, indent=2)

    def load(self, file: str):
        try:
            with open(file, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
        except FileNotFoundError:
            logger.warning("Corpus index file not found at %s — starting with empty chunk list.", file)
            self.chunks = []
        except json.JSONDecodeError:
            logger.error("Corpus index file at %s is corrupted (invalid JSON) — starting with empty chunk list.", file)
            self.chunks = []


