from core.models import Record


class Store:
    def __init__(self):
        self.records = []

    def add(self, record: Record) -> None:
        self.records.append(record)

    def all(self) -> list[Record]:
        return self.records
