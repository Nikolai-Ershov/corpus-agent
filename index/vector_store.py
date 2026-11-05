"""In-memory storage for embedded document chunks with JSON persistence."""

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
            "vector": vector.tolist(),
        }
        self.chunks.append(chunk_data)

    def save(self, path):
        # no try/except here on purpose: this runs during a manual index
        # build, and a failed save should crash loudly, not hide silently
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.chunks, file, ensure_ascii=False, indent=2)

    def load(self, file: str):
        # unlike save(), this runs when the bot starts up — it has to
        # degrade gracefully (empty index) instead of crashing the bot
        try:
            with open(file, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
        except FileNotFoundError:
            # expected on a first run, before any index has been built
            logger.warning("Corpus index file not found at %s — starting with empty chunk list.", file)
            self.chunks = []
        except json.JSONDecodeError:
            # not expected — the file exists but got corrupted somehow
            logger.error("Corpus index file at %s is corrupted (invalid JSON) — starting with empty chunk list.", file)
            self.chunks = []
