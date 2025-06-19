from server.models.user_model import User
from server.repository.db_connector import DBConnector
from typing import Optional


class UserRepository:
    def __init__(self, db: DBConnector):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return User(**row)
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return User(**row)
        return None

    def create_user(
        self, username: str, email: str, password_hash: str, is_admin=False
    ) -> int:
        conn = self.db.connect()
        cursor = conn.cursor()
        query = """
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (username, email, password_hash, is_admin))
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        return user_id

    def get_all_users(self):
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users"
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return [User(**row) for row in rows]

    def delete_user(self, user_id: int) -> bool:
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
