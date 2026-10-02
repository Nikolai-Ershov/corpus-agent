from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Record:
    content: str
    timestamp: datetime
    origin_ref: str = ""
    metadata: dict = field(default_factory=dict)
