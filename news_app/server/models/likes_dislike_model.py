from dataclasses import dataclass
from datetime import datetime


@dataclass
class LikesDislike:
    user_id: int
    article_id: int
    is_like: bool
    created_at: datetime
