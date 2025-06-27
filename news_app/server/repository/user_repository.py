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
        query = "SELECT * FROM users WHERE id = %s"
        with with_cursor(conn, dictionary=True) as cursor:
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
        return row_to_model(row, User)

    def get_user_by_email(self, email: str) -> Optional[User]:
        conn = self.db.connect()
        query = "SELECT * FROM users WHERE email = %s"
        with with_cursor(conn, dictionary=True) as cursor:
            cursor.execute(query, (email,))
            row = cursor.fetchone()
        return row_to_model(row, User)

    def create_user(
        self, username: str, email: str, password_hash: str, is_admin=False
    ) -> int:
        conn = self.db.connect()
        query = """
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (%s, %s, %s, %s)
        """
        with with_cursor(conn) as cursor:
            cursor.execute(query, (username, email, password_hash, is_admin))
            conn.commit()
            user_id = cursor.lastrowid
        return user_id

    def get_all_users(self) -> List[User]:
        conn = self.db.connect()
        query = "SELECT * FROM users"
        with with_cursor(conn, dictionary=True) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        return rows_to_models(rows, User)

    def delete_user(self, user_id: int) -> bool:
        conn = self.db.connect()
        query = "DELETE FROM users WHERE id = %s"

        def do_delete():
            with with_cursor(conn) as cursor:
                cursor.execute(query, (user_id,))
                conn.commit()
                return cursor.rowcount > 0

        return safe_execute(do_delete, default=False)
