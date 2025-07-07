from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Report:
    id: Optional[int]
    user_id: int
    article_id: int
    reason: Optional[str]
    created_at: Optional[datetime]
    status: str  # can be either -> 'pending' OR 'reviewed' OR 'auto-blocked'
