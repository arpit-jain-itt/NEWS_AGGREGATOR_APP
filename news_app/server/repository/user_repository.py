import json
from server.models.user_model import User
from server.repository.db_connector import DBConnector
from typing import Optional, List
from server.utils.repository_helper import (
    with_cursor,
    row_to_model,
    rows_to_models,
    safe_execute,
)


class UserRepository:
    def __init__(self, db: DBConnector):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        conn = self.db.connect()
        try:
            query = "SELECT * FROM users WHERE id = %s"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
            return row_to_model(row, User)
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        conn = self.db.connect()
        try:
            query = "SELECT * FROM users WHERE email = %s"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, (email,))
                row = cursor.fetchone()
            return row_to_model(row, User)
        finally:
            conn.close()

    def create_user(
        self, username: str, email: str, password_hash: str, is_admin=False
    ) -> int:
        conn = self.db.connect()
        try:
            query = """
                INSERT INTO users (username, email, password_hash, is_admin)
                VALUES (%s, %s, %s, %s)
            """
            with with_cursor(conn) as cursor:
                cursor.execute(
                    query, (username, email, password_hash, is_admin)
                )
                conn.commit()
                user_id = cursor.lastrowid
            return user_id
        finally:
            conn.close()

    def get_all_users(self) -> List[User]:
        conn = self.db.connect()
        try:
            query = "SELECT * FROM users"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            return rows_to_models(rows, User)
        finally:
            conn.close()

    def delete_user(self, user_id: int) -> bool:
        conn = self.db.connect()
        query = "DELETE FROM users WHERE id = %s"

        def do_delete():
            with with_cursor(conn) as cursor:
                cursor.execute(query, (user_id,))
                conn.commit()
                return cursor.rowcount > 0

        try:
            return safe_execute(do_delete, default=False)
        finally:
            conn.close()

    # PERSONALIZATION METHODS

    def get_user_keywords(self, user_id: int) -> List[str]:
        """
        Returns a list of keywords set by the user for notifications.
        Handles JSON object with 'keywords' key, JSON list, or comma-separated string.
        """
        conn = self.db.connect()
        try:
            query = (
                "SELECT keywords FROM user_notifications WHERE user_id = %s"
            )
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, (user_id,))
                row = cursor.fetchone()
            if row and row["keywords"]:
                try:
                    # Try to parse as JSON object with 'keywords' key
                    data = json.loads(row["keywords"])
                    if isinstance(data, dict) and "keywords" in data:
                        return [
                            kw.strip().lower()
                            for kw in data["keywords"]
                            if kw.strip()
                        ]
                    # Or as a list
                    if isinstance(data, list):
                        return [
                            kw.strip().lower() for kw in data if kw.strip()
                        ]
                except Exception:
                    # Fallback: split by comma
                    return [
                        kw.strip().lower()
                        for kw in row["keywords"].split(",")
                        if kw.strip()
                    ]
            return []
        finally:
            conn.close()

    def get_liked_article_ids(self, user_id: int) -> List[int]:
        """
        Returns a list of article IDs the user has liked.
        """
        conn = self.db.connect()
        try:
            query = "SELECT article_id FROM likes_dislikes WHERE user_id = %s AND is_like = TRUE"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, (user_id,))
                rows = cursor.fetchall()
            return [row["article_id"] for row in rows]
        finally:
            conn.close()

    def get_disliked_article_ids(self, user_id: int) -> List[int]:
        """
        Returns a list of article IDs the user has disliked.
        """
        conn = self.db.connect()
        try:
            query = "SELECT article_id FROM likes_dislikes WHERE user_id = %s AND is_like = FALSE"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, (user_id,))
                rows = cursor.fetchall()
            return [row["article_id"] for row in rows]
        finally:
            conn.close()

    def get_saved_article_ids(self, user_id: int) -> List[int]:
        """
        Returns a list of article IDs the user has saved.
        """
        conn = self.db.connect()
        try:
            query = "SELECT article_id FROM saved_articles WHERE user_id = %s"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, (user_id,))
                rows = cursor.fetchall()
            return [row["article_id"] for row in rows]
        finally:
            conn.close()

    def get_viewed_article_ids(self, user_id: int) -> List[int]:
        """
        Returns a list of article IDs the user has viewed.
        """
        conn = self.db.connect()
        try:
            query = "SELECT article_id FROM viewed_articles WHERE user_id = %s"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, (user_id,))
                rows = cursor.fetchall()
            return [row["article_id"] for row in rows]
        finally:
            conn.close()
