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
                timestamp=datetime.now(),
                origin_ref=filepath
            )

            records.append(record)

        return records





