from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Source:
    id: int
    name: str
    api_endpoint: str
    api_key: str
    active: bool = True
    last_accessed: Optional[datetime] = None
