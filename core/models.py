from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Record:
    """A single piece of source content before chunking (one note, one transcript)."""

    content: str
    timestamp: datetime

    # Which ingestion adapter and source this came from (e.g. a filename).
    # Optional because not every adapter can set it at creation time.
    origin_ref: str = ""

    # Arbitrary per-record extras (author, topic, etc.), optional and adapter-specific.
    # default_factory=dict, not {}, so each Record gets its own dict instance —
    # a shared mutable default would leak metadata between records.
    metadata: dict = field(default_factory=dict)
