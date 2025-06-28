from typing import List, Optional
from datetime import datetime, timezone
from server.models.article_model import Article
from server.repository.db_connector import DBConnector
from server.utils.repository_helper import with_cursor


class ArticleRepository:
    def __init__(self, db: DBConnector):
        self.db = db

    def get_article_by_id(
        self, article_id: int, include_hidden: bool = False
    ) -> Optional[Article]:
        conn = self.db.connect()
        try:
            query = """
                SELECT a.*, c.name AS category_name
                FROM articles a
                LEFT JOIN categories c ON a.category_id = c.id
                WHERE a.id = %s
            """
            params = [article_id]
            if not include_hidden:
                query += " AND a.is_hidden = FALSE"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, params)
                row = cursor.fetchone()
            if row:
                category_name = row.pop("category_name", None)
                article = Article(**row)
                setattr(article, "category_name", category_name)
                return article
            return None
        finally:
            conn.close()

    def get_articles_by_category(
        self, category_id: int, limit=20, offset=0, include_hidden: bool = False
    ) -> List[Article]:
        conn = self.db.connect()
        try:
            query = """
                SELECT a.*, c.name AS category_name
                FROM articles a
                LEFT JOIN categories c ON a.category_id = c.id
                WHERE a.category_id = %s
            """
            params = [category_id]
            if not include_hidden:
                query += " AND a.is_hidden = FALSE"
            query += " ORDER BY a.published_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
            return self._build_articles(rows)
        finally:
            conn.close()

    def get_articles_by_ids(
        self, article_ids: List[int], include_hidden: bool = False
    ) -> List[Article]:
        if not article_ids:
            return []
        conn = self.db.connect()
        try:
            format_strings = ",".join(["%s"] * len(article_ids))
            query = f"""
                SELECT a.*, c.name AS category_name
                FROM articles a
                LEFT JOIN categories c ON a.category_id = c.id
                WHERE a.id IN ({format_strings})
            """
            params = list(article_ids)
            if not include_hidden:
                query += " AND a.is_hidden = FALSE"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
            return self._build_articles(rows)
        finally:
            conn.close()

    def get_next_article_id(self) -> int:
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT MAX(id) FROM articles")
            max_id_row = cursor.fetchone()
            max_article_id = max_id_row[0] if max_id_row[0] is not None else 0

            cursor.execute(
                "SELECT last_used FROM article_sequence WHERE id = 1 FOR UPDATE"
            )
            seq_row = cursor.fetchone()
            last_used = seq_row[0] if seq_row else 0

            next_id = max(max_article_id, last_used) + 1
            cursor.execute(
                "UPDATE article_sequence SET last_used = %s WHERE id = 1", (next_id,)
            )
            conn.commit()
            return next_id
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to get next article ID: {e}")
        finally:
            cursor.close()
            conn.close()

    def insert_article(
        self,
        title: str,
        description: str,
        content: Optional[str],
        url: str,
        published_at: datetime,
        source_id: int,
        category_id: int,
    ) -> int:
        conn = self.db.connect()
        try:
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute("SELECT id FROM articles WHERE url = %s", (url,))
                existing = cursor.fetchone()
            if existing:
                return existing["id"]

            article_id = self.get_next_article_id()
            query = """
                INSERT INTO articles (id, title, description, content, url, published_at, source_id, category_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            with with_cursor(conn) as insert_cursor:
                insert_cursor.execute(
                    query,
                    (
                        article_id,
                        title,
                        description,
                        content,
                        url,
                        published_at,
                        source_id,
                        category_id,
                    ),
                )
                conn.commit()
            return article_id
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Failed to insert article: {e}")
            raise
        finally:
            conn.close()

    def get_latest_articles(
        self, limit=20, offset=0, include_hidden: bool = False
    ) -> List[Article]:
        conn = self.db.connect()
        try:
            query = """
                SELECT a.*, c.name AS category_name
                FROM articles a
                LEFT JOIN categories c ON a.category_id = c.id
            """
            if not include_hidden:
                query += " WHERE a.is_hidden = FALSE"
            query += " ORDER BY a.published_at DESC LIMIT %s OFFSET %s"
            params = [limit, offset]
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
            return self._build_articles(rows)
        finally:
            conn.close()

    def search_articles(
        self,
        keyword: str = "",
        category_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 20,
        offset: int = 0,
        include_hidden: bool = False,
    ) -> List[Article]:
        conn = self.db.connect()
        try:
            query = """
                SELECT a.*, c.name AS category_name
                FROM articles a
                LEFT JOIN categories c ON a.category_id = c.id
                WHERE 1=1
            """
            params = []

            if not include_hidden:
                query += " AND a.is_hidden = FALSE"

            if category_id is not None:
                query += " AND a.category_id = %s"
                params.append(category_id)

            if keyword:
                query += " AND (LOWER(a.title) LIKE %s OR LOWER(a.description) LIKE %s OR LOWER(a.content) LIKE %s)"
                like_keyword = f"%{keyword.lower()}%"
                params.extend([like_keyword, like_keyword, like_keyword])

            if start_date and start_date.tzinfo is None:
                start_date = start_date.replace(tzinfo=timezone.utc)
            if end_date and end_date.tzinfo is None:
                end_date = end_date.replace(tzinfo=timezone.utc)

            if start_date and end_date:
                query += " AND a.published_at BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            elif start_date:
                query += " AND a.published_at >= %s"
                params.append(start_date)
            elif end_date:
                query += " AND a.published_at <= %s"
                params.append(end_date)

            query += " ORDER BY a.published_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
            return self._build_articles(rows)
        finally:
            conn.close()

    def is_article_saved_by_user(self, user_id: int, article_id: int) -> bool:
        conn = self.db.connect()
        try:
            with with_cursor(conn) as cursor:
                cursor.execute(
                    "SELECT 1 FROM saved_articles WHERE user_id = %s AND article_id = %s",
                    (user_id, article_id),
                )
                result = cursor.fetchone()
            return result is not None
        finally:
            conn.close()

    def save_article_for_user(self, user_id: int, article_id: int) -> str:
        if self.is_article_saved_by_user(user_id, article_id):
            return "already_saved"
        conn = self.db.connect()
        try:
            with with_cursor(conn) as cursor:
                cursor.execute(
                    "INSERT INTO saved_articles (user_id, article_id, saved_at) VALUES (%s, %s, NOW())",
                    (user_id, article_id),
                )
                conn.commit()
            return "saved"
        except Exception:
            conn.rollback()
            return "error"
        finally:
            conn.close()

    def remove_saved_article(self, user_id: int, article_id: int) -> str:
        conn = self.db.connect()
        try:
            with with_cursor(conn) as cursor:
                cursor.execute(
                    "DELETE FROM saved_articles WHERE user_id = %s AND article_id = %s",
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
            conn.close()

    def get_saved_articles_by_user(
        self, user_id: int, limit=20, offset=0, include_hidden: bool = False
    ) -> List[Article]:
        conn = self.db.connect()
        try:
            query = """
                SELECT a.*, c.name AS category_name
                FROM saved_articles sa
                JOIN articles a ON sa.article_id = a.id
                LEFT JOIN categories c ON a.category_id = c.id
                WHERE sa.user_id = %s
            """
            params = [user_id]
            if not include_hidden:
                query += " AND a.is_hidden = FALSE"
            query += " ORDER BY sa.saved_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
            return self._build_articles(rows)
        finally:
            conn.close()

    def get_headlines(
        self,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        limit: int = 20,
        offset: int = 0,
        include_hidden: bool = False,
    ) -> List[Article]:
        conn = self.db.connect()
        try:
            query = """
                SELECT a.*, c.name AS category_name
                FROM articles a
                LEFT JOIN categories c ON a.category_id = c.id
                WHERE 1 = 1
            """
            params = []

            if not include_hidden:
                query += " AND a.is_hidden = FALSE"

            if start_date and end_date:
                query += " AND DATE(a.published_at) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            elif start_date:
                query += " AND DATE(a.published_at) >= %s"
                params.append(start_date)
            elif end_date:
                query += " AND DATE(a.published_at) <= %s"
                params.append(end_date)

            query += " ORDER BY a.published_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
            return self._build_articles(rows)
        finally:
            conn.close()

    def set_article_hidden(self, article_id: int, is_hidden: bool) -> bool:
        conn = self.db.connect()
        try:
            with with_cursor(conn) as cursor:
                cursor.execute(
                    "UPDATE articles SET is_hidden = %s WHERE id = %s",
                    (is_hidden, article_id),
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()

    def _build_articles(self, rows: List[dict]) -> List[Article]:
        articles = []
        for row in rows:
            category_name = row.pop("category_name", None)
            article = Article(**row)
            setattr(article, "category_name", category_name)
            articles.append(article)
        return articles

    def get_blocked_articles(self) -> List[Article]:
        conn = self.db.connect()
        try:
            query = """
                SELECT a.*, c.name AS category_name
                FROM articles a
                LEFT JOIN categories c ON a.category_id = c.id
                WHERE a.is_hidden = TRUE
                ORDER BY a.published_at DESC
            """
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            return self._build_articles(rows)
        finally:
            conn.close()

    # PERSONALIZATION SUPPORT

    def get_recent_visible_articles(self, limit: int = 100) -> List[dict]:
        """
        Returns recent, visible articles as a list of dicts (for scoring).
        """
        conn = self.db.connect()
        try:
            query = """
                SELECT a.*, c.name AS category_name
                FROM articles a
                LEFT JOIN categories c ON a.category_id = c.id
                WHERE a.is_hidden = FALSE
                ORDER BY a.published_at DESC
                LIMIT %s
            """
            params = [limit]
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
            return rows
        finally:
            conn.close()
