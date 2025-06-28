from typing import List
from server.models.keyword_filter_model import KeywordFilter
from server.utils.repository_helper import (
    with_cursor,
    rows_to_models,
    safe_execute,
)


class KeywordFilterRepository:
    def __init__(self, db):
        self.db = db

    def add_keyword(self, keyword: str) -> bool:
        query = "INSERT INTO keyword_filters (keyword, active) VALUES (%s, TRUE) ON DUPLICATE KEY UPDATE active=TRUE"

        def do_add():
            conn = self.db.connect()
            try:
                with with_cursor(conn) as cursor:
                    cursor.execute(query, (keyword,))
                    conn.commit()
                    return True
            finally:
                conn.close()

        return safe_execute(do_add, default=False)

    def get_all_keywords(
        self, active_only: bool = True
    ) -> List[KeywordFilter]:
        query = "SELECT * FROM keyword_filters"
        if active_only:
            query += " WHERE active=TRUE"
        conn = self.db.connect()
        try:
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            return rows_to_models(rows, KeywordFilter)
        finally:
            conn.close()

    def block_keyword(self, keyword: str) -> bool:
        query = "UPDATE keyword_filters SET active=FALSE WHERE keyword=%s"

        def do_block():
            conn = self.db.connect()
            try:
                with with_cursor(conn) as cursor:
                    cursor.execute(query, (keyword,))
                    conn.commit()
                    return True
            finally:
                conn.close()

        return safe_execute(do_block, default=False)

    def unblock_keyword(self, keyword: str) -> bool:
        query = "UPDATE keyword_filters SET active=TRUE WHERE keyword=%s"

        def do_unblock():
            conn = self.db.connect()
            try:
                with with_cursor(conn) as cursor:
                    cursor.execute(query, (keyword,))
                    conn.commit()
                    return True
            finally:
                conn.close()

        return safe_execute(do_unblock, default=False)

    def delete_keyword(self, keyword: str) -> bool:
        query = "DELETE FROM keyword_filters WHERE keyword=%s"

        def do_delete():
            conn = self.db.connect()
            try:
                with with_cursor(conn) as cursor:
                    cursor.execute(query, (keyword,))
                    conn.commit()
                    return True
            finally:
                conn.close()

        return safe_execute(do_delete, default=False)
