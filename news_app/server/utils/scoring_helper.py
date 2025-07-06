from datetime import datetime, timezone
from typing import List, Optional, Dict
import math


class ScoringHelper:
    """
    Utility class that provides static methods for scoring
    articles based on user behavior.
    """

    @staticmethod
    def keyword_score(article_keywords: List[str], user_keywords: List[str]) -> float:
        """
        Score based on keyword overlap between article and
        user-preferred keywords.
        Returns a float between 0 and 1.
        """
        if not article_keywords or not user_keywords:
            return 0.0

        match_count = len(set(article_keywords) & set(user_keywords))
        return match_count / len(set(user_keywords))

    @staticmethod
    def like_bonus(is_liked: bool) -> float:
        """
        Provide a bonus if similar article was liked in the past.
        """
        return 0.5 if is_liked else 0.0

    @staticmethod
    def view_penalty(viewed: bool) -> float:
        """
        Penalize already viewed articles.
        """
        return -0.7 if viewed else 0.0

    @staticmethod
    def save_bonus(saved: bool) -> float:
        """
        Bonus for categories or sources the user tends to save.
        """
        return 0.3 if saved else 0.0

    @staticmethod
    def recency_score(
        published_at: datetime, current_time: Optional[datetime] = None
    ) -> float:
        """
        Score articles based on recency. The more recent, the higher the score.
        Exponential decay to reduce impact of older articles.
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        if (
            published_at.tzinfo is None
            or published_at.tzinfo.utcoffset(published_at) is None
        ):
            published_at = published_at.replace(tzinfo=timezone.utc)

        delta_hours = (current_time - published_at).total_seconds() / 3600.0
        return math.exp(-delta_hours / 24.0)

    @staticmethod
    def final_score(weights: Dict[str, float]) -> float:
        """
        Aggregate score using weights.
        """
        return (
            0.4 * weights.get("keyword", 0)
            + 0.2 * weights.get("recency", 0)
            + 0.15 * weights.get("like_bonus", 0)
            + 0.15 * weights.get("save_bonus", 0)
            + 0.1 * weights.get("view_penalty", 0)
        )
