from typing import List, Optional
from datetime import datetime
from server.models.source_model import Source
from server.repository.db_connector import DBConnector


class SourceRepository:
    """
    Data‑access layer for the `sources` table.
    """

    def __init__(self, db: DBConnector):
        self.db = db

    def get_active_source(self) -> Optional[Source]:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sources WHERE active = TRUE LIMIT 1")
        row = cursor.fetchone()
        cursor.close()
        return Source(**row) if row else None

    def get_all_sources(self) -> List[Source]:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sources ORDER BY id")
        rows = cursor.fetchall()
        cursor.close()
        return [Source(**row) for row in rows] if rows else []

    def update_last_accessed(self, source_id: int, accessed_at: datetime):
        conn = self.db.connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sources SET last_accessed = %s WHERE id = %s",
            (accessed_at, source_id),
        )
        conn.commit()
        cursor.close()

    def set_active_source(self, source_id: int) -> bool:
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
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
            cursor.close()

    def add_source(self, name: str) -> bool:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT 1 FROM sources WHERE name = %s", (name,))
            if cursor.fetchone():
                return False  # already iit is there

            cursor.execute(
                "INSERT INTO sources (name, active, last_accessed) VALUES (%s, FALSE, NULL)",
                (name,),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"[Error] Could not add source '{name}': {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()

    def remove_source(self, source_id: int) -> bool:
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM sources WHERE id = %s", (source_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Could not remove source with id {source_id}: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
