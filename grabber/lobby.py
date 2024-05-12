from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Lobby:
    timestamp_raw: str
    mp_id: int
    timestamp: datetime = field(init=False)

    def __post_init__(self):
        self.timestamp = datetime.fromisoformat(self.timestamp_raw)
