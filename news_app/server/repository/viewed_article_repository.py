from typing import List
from server.repository.db_connector import DBConnector
from server.utils.repository_helper import (
    with_cursor,
    safe_execute,
)


class ViewedArticleRepository:
    def __init__(self, db: DBConnector):
        self.db = db

    def mark_viewed(self, user_id: int, article_id: int) -> None:
        conn = self.db.connect()
        try:

            def do_mark():
                with with_cursor(conn) as cursor:
                    cursor.execute(
                        """
                        INSERT IGNORE INTO viewed_articles (user_id, article_id, viewed_at)
                        VALUES (%s, %s, UTC_TIMESTAMP())
                        """,
                        (user_id, article_id),
                    )
                    conn.commit()

            safe_execute(do_mark)
        finally:
            conn.close()

    def get_viewed_article_ids_by_user(self, user_id: int) -> List[int]:
        conn = self.db.connect()
        try:
            with with_cursor(conn) as cursor:
                cursor.execute(
                    "SELECT article_id FROM viewed_articles WHERE user_id = %s",
                    (user_id,),
                )
                rows = cursor.fetchall()
            return [row[0] for row in rows]
        finally:
            conn.close()
