from dataclasses import dataclass
from datetime import datetime


@dataclass
class ViewedArticle:
    user_id: int
    article_id: int
    viewed_at: datetime
