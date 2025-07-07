from typing import List, Optional
from datetime import datetime
from server.models.source_model import Source
from server.repository.db_connector import DBConnector
from server.utils.repository_helper import (
    with_cursor,
    rows_to_models,
    row_to_model,
    safe_execute,
)


class SourceRepository:
    def __init__(self, db: DBConnector):
        self.db = db

    def _get_connection(self):
        conn = self.db.connect()
        if conn is None or not conn.is_connected():
            raise RuntimeError(
                "DB connection is not available"
            )
        return conn

    def get_active_source(self) -> Optional[Source]:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM sources WHERE active = TRUE LIMIT 1"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
            return row_to_model(row, Source)
        finally:
            conn.close()

    def get_all_sources(self) -> List[Source]:
        conn = self._get_connection()
        try:
            query = "SELECT * FROM sources ORDER BY id"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            return rows_to_models(rows, Source)
        finally:
            conn.close()

    def update_last_accessed(self, source_id: int, accessed_at: datetime):
        conn = self._get_connection()
        try:
            with with_cursor(conn) as cursor:
                cursor.execute(
                    "UPDATE sources SET last_accessed = %s WHERE id = %s",
                    (accessed_at, source_id),
                )
                conn.commit()
        finally:
            conn.close()

    def set_active_source(self, source_id: int) -> bool:
        def do_set_active():
            try:
                conn = self._get_connection()
            except RuntimeError as e:
                print(f"{e}")
                return False
            try:
                with with_cursor(conn) as cursor:
                    cursor.execute(
                        """
                        UPDATE sources
                        SET active = CASE WHEN id = %s THEN TRUE ELSE FALSE END
                        """,
                        (source_id,),
                    )
                    conn.commit()
                    return cursor.rowcount > 0
            finally:
                conn.close()

        return safe_execute(do_set_active, default=False)

    def add_source(self, name: str) -> bool:
        def do_add():
            try:
                conn = self._get_connection()
            except RuntimeError as e:
                print(f"[SourceRepository] {e}")
                return False
            try:
                with with_cursor(conn, dictionary=True) as cursor:
                    cursor.execute(
                        "SELECT 1 FROM sources WHERE name = %s", (name,)
                    )
                    if cursor.fetchone():
                        return False  # already exists
                    cursor.execute(
                        "INSERT INTO sources (name, active, last_accessed) VALUES (%s, FALSE, NULL)",
                        (name,),
                    )
                    conn.commit()
                    return True
            finally:
                conn.close()

        return safe_execute(do_add, default=False)

    def remove_source(self, source_id: int) -> bool:
        def do_remove():
            try:
                conn = self._get_connection()
            except RuntimeError as e:
                print(f"{e}")
                return False
            try:
                with with_cursor(conn) as cursor:
                    cursor.execute(
                        "DELETE FROM sources WHERE id = %s", (source_id,)
                    )
                    conn.commit()
                    return cursor.rowcount > 0
            finally:
                conn.close()

        return safe_execute(do_remove, default=False)
