from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Record:
    content: str
    source: str
    timestamp: datetime
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    origin_ref: str = ""
    metadata: dict = field(default_factory=dict)
