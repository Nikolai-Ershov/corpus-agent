from abc import ABC, abstractmethod
from core.models import Record


class Adapter(ABC):
    @abstractmethod
    def parse(self, raw) -> list[Record]:
        pass



