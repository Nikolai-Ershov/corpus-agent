"""Shared contract every adapter must implement.

Kept as its own file, not folded into plaintext.py: future adapters
(markdown, JSON, whatever else) should import this base class directly,
not reach into one specific implementation to get it."""

from abc import ABC, abstractmethod
from core.models import Record


class Adapter(ABC):
    @abstractmethod
    def parse(self, raw) -> list[Record]:
        pass