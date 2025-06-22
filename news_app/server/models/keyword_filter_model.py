from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class KeywordFilter:
    id: Optional[int]
    keyword: str
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
