"""Plaintext note adapter: read every .txt file in a directory and turn
each one into a Record."""

from ingestion.base import Adapter
from core.models import Record
from datetime import datetime
import os


class PlaintextAdapter(Adapter):
    def parse(self, raw: str) -> list[Record]:
        records = []
        paths = os.listdir(raw)

        for filename in paths:
            if not filename.endswith(".txt"):
                continue

            filepath = os.path.join(raw, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()

            record = Record(
                content=content,
                # Record requires a timestamp with no default — this is
                # "when we indexed it", not a meaningful date about the
                # file itself, and nothing downstream reads it yet
                timestamp=datetime.now(),
                origin_ref=filepath
            )

            records.append(record)

        return records



