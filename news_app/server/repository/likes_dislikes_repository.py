from typing import List, Tuple, Optional, Any
from server.models.article_model import Article
from server.repository.db_connector import DBConnector
from server.utils.repository_helper import with_cursor


class LikesDislikesRepository:
    def __init__(self, db: DBConnector):
        self.db = db

    def upsert_reaction(self, user_id: int, article_id: int, is_like: bool) -> str:
        query_update = """
            UPDATE likes_dislikes
            SET is_like = %s, created_at = NOW()
            WHERE user_id = %s AND article_id = %s
        """
        query_insert = """
            INSERT INTO likes_dislikes (user_id, article_id, is_like, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        conn = self.db.connect()
        try:
            affected = self._run_write(
                conn, query_update, (is_like, user_id, article_id)
            )
            if affected == 0:
                self._run_write(conn, query_insert, (user_id, article_id, is_like))
                return "created"
            return "updated"
        except Exception:
            return "error"

    def delete_reaction(self, user_id: int, article_id: int) -> str:
        query = "DELETE FROM likes_dislikes WHERE user_id = %s AND article_id = %s"
        conn = self.db.connect()
        try:
            affected = self._run_write(conn, query, (user_id, article_id))
            return "deleted" if affected else "not_found"
        except Exception:
            return "error"

    def remove_like(self, user_id: int, article_id: int) -> str:
        return self._remove_specific_reaction(user_id, article_id, True)

    def remove_dislike(self, user_id: int, article_id: int) -> str:
        return self._remove_specific_reaction(user_id, article_id, False)

    def get_user_reaction(self, user_id: int, article_id: int) -> Optional[bool]:
        query = (
            "SELECT is_like FROM likes_dislikes WHERE user_id = %s AND article_id = %s"
        )
        row = self._run_fetchone(query, (user_id, article_id))
        if row is None:
            return None
        return bool(row[0])

    def get_reaction_summary(self, user_id: int) -> Tuple[int, int]:
        query = """
            SELECT
              SUM(is_like = 1) AS likes,
              SUM(is_like = 0) AS dislikes
            FROM likes_dislikes
            WHERE user_id = %s
        """
        row = self._run_fetchone(query, (user_id,))
        likes, dislikes = row if row else (0, 0)
        return likes or 0, dislikes or 0

    def get_reacted_articles(
        self,
        user_id: int,
        is_like: bool,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Article]:
        query = """
            SELECT a.*, c.name AS category_name
            FROM likes_dislikes ld
            JOIN articles a        ON ld.article_id = a.id
            LEFT JOIN categories c ON a.category_id = c.id
            WHERE ld.user_id = %s
              AND ld.is_like = %s
            ORDER BY ld.created_at DESC
            LIMIT %s OFFSET %s
        """
        conn = self.db.connect()
        with with_cursor(conn, dictionary=True) as cursor:
            cursor.execute(query, (user_id, is_like, limit, offset))
            rows = cursor.fetchall()
        return self._build_articles(rows)

    def _remove_specific_reaction(
        self, user_id: int, article_id: int, is_like: bool
    ) -> str:
        query = """
            DELETE FROM likes_dislikes
            WHERE user_id = %s AND article_id = %s AND is_like = %s
        """
        conn = self.db.connect()
        try:
            affected = self._run_write(conn, query, (user_id, article_id, is_like))
            return "deleted" if affected else "not_found"
        except Exception:
            return "error"

    def _run_write(self, conn, query: str, params: tuple) -> int:
        with with_cursor(conn) as cursor:
            cursor.execute(query, params)
            affected = cursor.rowcount
            conn.commit()
            return affected

    def _run_fetchone(self, query: str, params: tuple) -> Optional[Any]:
        conn = self.db.connect()
        with with_cursor(conn) as cursor:
            cursor.execute(query, params)
            row = cursor.fetchone()
        return row

    def _build_articles(self, rows: List[dict]) -> List[Article]:
        articles: List[Article] = []
        for row in rows:
            category_name = row.pop("category_name", None)
            article = Article(**row)
            setattr(article, "category_name", category_name)
            articles.append(article)
        return articles

    def get_article_reactions_count(self, article_id: int) -> dict:
        query = """
            SELECT is_like, COUNT(*) as count
            FROM likes_dislikes
            WHERE article_id = %s
            GROUP BY is_like
        """
        conn = self.db.connect()
        with with_cursor(conn, dictionary=True) as cursor:
            cursor.execute(query, (article_id,))
            rows = cursor.fetchall()
        summary = {"likes": 0, "dislikes": 0}
        for row in rows:
            if row["is_like"]:
                summary["likes"] = row["count"]
            else:
                summary["dislikes"] = row["count"]
        return summary
