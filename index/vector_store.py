import json
import uuid


class VectorStore:
    def __init__(self):
        self.chunks = []

    def add(self, record_id, text, vector):

        chunk_data = {
            "chunk_id": str(uuid.uuid4()),
            "record_id": record_id,
            "text": text,
            "vector": vector.tolist()
        }

        self.chunks.append(chunk_data)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.chunks, file, ensure_ascii=False, indent=2)

    def load(self, file: str):
        try:
            with open(file, "r") as f:
                self.chunks = json.load(f)
        except FileNotFoundError:
            self.chunks = []
        except json.JSONDecodeError:
            print("Warning: data file is corrupted. Starting with empty list.")
            self.chunks = []


