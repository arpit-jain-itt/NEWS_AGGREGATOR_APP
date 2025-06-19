from typing import List, Tuple
from datetime import datetime
from server.models.article_model import Article
from server.repository.db_connector import DBConnector


class LikesDislikesRepository:
    def __init__(self, db: DBConnector):
        self.db = db

    def upsert_reaction(self, user_id: int, article_id: int, is_like: bool) -> str:
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE likes_dislikes
                SET is_like = %s, created_at = NOW()
                WHERE user_id = %s AND article_id = %s
                """,
                (is_like, user_id, article_id),
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO likes_dislikes
                        (user_id, article_id, is_like, created_at)
                    VALUES (%s, %s, %s, NOW())
                    """,
                    (user_id, article_id, is_like),
                )
                conn.commit()
                return "created"
            conn.commit()
            return "updated"
        except Exception:
            conn.rollback()
            return "error"
        finally:
            cursor.close()

    def delete_reaction(self, user_id: int, article_id: int) -> str:
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM likes_dislikes WHERE user_id=%s AND article_id=%s",
                (user_id, article_id),
            )
            if cursor.rowcount == 0:
                conn.rollback()
                return "not_found"
            conn.commit()
            return "deleted"
        except Exception:
            conn.rollback()
            return "error"
        finally:
            cursor.close()

    def get_reaction_summary(self, user_id: int) -> Tuple[int, int]:
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
              SUM(is_like = 1) AS likes,
              SUM(is_like = 0) AS dislikes
            FROM likes_dislikes
            WHERE user_id = %s
            """,
            (user_id,),
        )
        likes, dislikes = cursor.fetchone()
        cursor.close()
        return likes or 0, dislikes or 0

    def get_reacted_articles(
        self,
        user_id: int,
        is_like: bool,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Article]:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT a.*, c.name AS category_name
            FROM likes_dislikes ld
            JOIN articles a          ON ld.article_id = a.id
            LEFT JOIN categories c   ON a.category_id = c.id
            WHERE ld.user_id = %s
              AND ld.is_like = %s
            ORDER BY ld.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (user_id, is_like, limit, offset),
        )
        rows = cursor.fetchall()
        cursor.close()
        return self._build_articles(rows)

    def _build_articles(self, rows: List[dict]) -> List[Article]:
        articles: List[Article] = []
        for row in rows:
            category_name = row.pop("category_name", None)
            article = Article(**row)
            setattr(article, "category_name", category_name)
            articles.append(article)
        return articles
