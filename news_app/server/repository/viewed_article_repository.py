from typing import List
from server.repository.db_connector import DBConnector


class ViewedArticleRepository:
    def __init__(self, db: DBConnector):
        self.db = db

    def mark_viewed(self, user_id: int, article_id: int) -> None:
        conn = self.db.connect()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT IGNORE INTO viewed_articles (user_id, article_id, viewed_at)
                VALUES (%s, %s, UTC_TIMESTAMP())
                """,
                (user_id, article_id),
            )
        conn.commit()

    def get_viewed_article_ids_by_user(self, user_id: int) -> List[int]:
        conn = self.db.connect()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT article_id FROM viewed_articles WHERE user_id = %s", (user_id,)
            )
            rows = cursor.fetchall()

        return [row[0] for row in rows]
