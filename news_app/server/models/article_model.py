from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    id: int
    title: str
    description: Optional[str]
    content: Optional[str]
    url: str
    published_at: datetime
    source_id: int
    category_id: int
