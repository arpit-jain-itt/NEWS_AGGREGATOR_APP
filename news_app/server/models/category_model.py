from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Category:
    id: int
    name: str
    is_hidden: bool = False
    updated_at: Optional[datetime] = None
