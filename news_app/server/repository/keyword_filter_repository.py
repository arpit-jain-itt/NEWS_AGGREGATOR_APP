from typing import List
from server.models.keyword_filter_model import KeywordFilter


class KeywordFilterRepository:
    def __init__(self, db):
        self.db = db

    def add_keyword(self, keyword: str) -> bool:
        query = "INSERT INTO keyword_filters (keyword, active) VALUES (%s, TRUE) ON DUPLICATE KEY UPDATE active=TRUE"
        conn = self.db.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (keyword,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding keyword: {e}")
            return False

    def get_all_keywords(self, active_only: bool = True) -> List[KeywordFilter]:
        query = "SELECT * FROM keyword_filters"
        if active_only:
            query += " WHERE active=TRUE"
        conn = self.db.connect()
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        return [KeywordFilter(**row) for row in rows]

    def block_keyword(self, keyword: str) -> bool:
        query = "UPDATE keyword_filters SET active=FALSE WHERE keyword=%s"
        conn = self.db.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (keyword,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error blocking keyword: {e}")
            return False

    def unblock_keyword(self, keyword: str) -> bool:
        query = "UPDATE keyword_filters SET active=TRUE WHERE keyword=%s"
        conn = self.db.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (keyword,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error unblocking keyword: {e}")
            return False

    def delete_keyword(self, keyword: str) -> bool:
        query = "DELETE FROM keyword_filters WHERE keyword=%s"
        conn = self.db.connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (keyword,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting keyword: {e}")
            return False
