from datetime import datetime
from typing import List, Dict, Any
from server.utils.scoring_helper import ScoringHelper


class PersonalizationService:
    def __init__(self, user_repo, article_repo):
        self.user_repo = user_repo
        self.article_repo = article_repo

    def get_personalized_articles(
        self, user_id: int, limit: int = 10, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Return top-N personalized articles for a user, ranked by computed score.
        If the user has no history, return the most recent articles.
        Supports pagination via limit and offset.
        """
        print(f"[Personalization] user_id={user_id}, limit={limit}, offset={offset}")

        # 1. Gather user behavior data
        user_keywords = self.user_repo.get_user_keywords(user_id) or []
        liked_article_ids = self.user_repo.get_liked_article_ids(user_id) or []
        saved_article_ids = self.user_repo.get_saved_article_ids(user_id) or []
        viewed_article_ids = self.user_repo.get_viewed_article_ids(user_id) or []

        print(f"[Personalization] User keywords: {user_keywords}")
        print(f"[Personalization] Liked articles: {liked_article_ids}")
        print(f"[Personalization] Saved articles: {saved_article_ids}")
        print(f"[Personalization] Viewed articles: {viewed_article_ids}")

        # 2. Fetch candidate articles
        candidate_articles = self.article_repo.get_recent_visible_articles()
        print(
            f"[Personalization] Fetched {len(candidate_articles)} candidate articles."
        )

        # Cold start: If user has no signals, just return recent articles
        if not (
            user_keywords
            or liked_article_ids
            or saved_article_ids
            or viewed_article_ids
        ):
            print(
                "[Personalization] No user signals found. Returning recent articles (cold start)."
            )
            return candidate_articles[offset : offset + limit]

        ranked_articles = []
        now = datetime.utcnow()

        for article in candidate_articles:
            article_keywords = self.extract_keywords(article)

            weights = {
                "keyword": ScoringHelper.keyword_score(article_keywords, user_keywords),
                "recency": ScoringHelper.recency_score(article["published_at"], now),
                "like_bonus": ScoringHelper.like_bonus(
                    article["id"] in liked_article_ids
                ),
                "save_bonus": ScoringHelper.save_bonus(
                    article["id"] in saved_article_ids
                ),
                "view_penalty": ScoringHelper.view_penalty(
                    article["id"] in viewed_article_ids
                ),
            }

            score = ScoringHelper.final_score(weights)
            print(
                f"[Scoring] Article ID: {article['id']} | Title: {article.get('title', '')[:40]}... | "
                f"Weights: {weights} | Score: {score}"
            )
            ranked_articles.append((score, article))

        # 3. Sort by score descending and return paginated results
        ranked_articles.sort(key=lambda x: x[0], reverse=True)
        print("[Personalization] Top articles returned:")
        for i, (score, article) in enumerate(
            ranked_articles[offset : offset + limit], 1
        ):
            print(
                f"  {i}. ID: {article['id']} | Score: {score} | Title: {article.get('title', '')[:40]}..."
            )

        return [article for _, article in ranked_articles[offset : offset + limit]]

    def extract_keywords(self, article: Dict[str, Any]) -> List[str]:
        """
        Very basic keyword extraction from title + description.
        Replace this with NLP later if needed.
        """
        title = article.get("title") or ""
        description = article.get("description") or ""
        text = (title + " " + description).lower()
        words = [word.strip(".,!?()[]") for word in text.split()]
        return [w for w in words if len(w) > 3]
