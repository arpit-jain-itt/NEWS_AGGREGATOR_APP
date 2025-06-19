from typing import List, Optional, Dict
from datetime import datetime, timezone
from server.models.notification_model import UserNotification
from server.repository.db_connector import DBConnector


class NotificationRepository:
    def __init__(self, db: DBConnector):
        self.db = db

    def get_notifications_for_user(self, user_id: int) -> List[UserNotification]:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            query = (
                "SELECT * FROM user_notifications WHERE user_id = %s AND enabled = TRUE"
            )
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            return [UserNotification(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def get_all_enabled_notifications(self) -> List[UserNotification]:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            query = "SELECT * FROM user_notifications WHERE enabled = TRUE"
            cursor.execute(query)
            rows = cursor.fetchall()
            return [UserNotification(**row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    def create_or_update_notification(
        self,
        user_id: int,
        keywords: str,
        notify_via_email: bool = True,
        enabled: bool = True,
    ) -> int:
        conn = self.db.connect()
        cursor = conn.cursor(buffered=True)
        try:
            query_select = "SELECT id FROM user_notifications WHERE user_id = %s"
            cursor.execute(query_select, (user_id,))
            row = cursor.fetchone()
            if row:
                notification_id = row[0]
                query_update = """
                    UPDATE user_notifications
                    SET keywords = %s, notify_via_email = %s, enabled = %s
                    WHERE id = %s
                """
                cursor.execute(
                    query_update, (keywords, notify_via_email, enabled, notification_id)
                )
            else:
                query_insert = """
                    INSERT INTO user_notifications (user_id, keywords, notify_via_email, enabled)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(
                    query_insert, (user_id, keywords, notify_via_email, enabled)
                )
                notification_id = cursor.lastrowid
            conn.commit()
            return notification_id
        finally:
            cursor.close()
            conn.close()

    def get_notification_by_user_id(self, user_id: int) -> Optional[UserNotification]:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            query = "SELECT * FROM user_notifications WHERE user_id = %s LIMIT 1"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            if row:
                return UserNotification(**row)
            return None
        finally:
            cursor.close()
            conn.close()

    def get_notification_preferences(self, user_id: int) -> Optional[Dict]:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            query = """
                SELECT id, keywords, notify_via_email, enabled
                FROM user_notifications
                WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            if rows:
                rows_sorted = sorted(rows, key=lambda x: x["id"], reverse=True)
                latest_row = rows_sorted[0]
                return {
                    "keywords": latest_row["keywords"],
                    "notify_via_email": bool(latest_row["notify_via_email"]),
                    "enabled": bool(latest_row["enabled"]),
                }
            return None
        finally:
            cursor.close()
            conn.close()

    def update_notification_preferences(
        self, user_id: int, keywords: str, notify_via_email: bool, enabled: bool
    ) -> bool:
        conn = self.db.connect()
        cursor = conn.cursor(buffered=True)
        try:
            query = """
                INSERT INTO user_notifications
                (user_id, keywords, notify_via_email, enabled)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    keywords = VALUES(keywords),
                    notify_via_email = VALUES(notify_via_email),
                    enabled = VALUES(enabled)
            """
            cursor.execute(query, (user_id, keywords, notify_via_email, enabled))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error updating notification preferences: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def get_last_notification_time(self, user_id: int) -> Optional[datetime]:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True, buffered=True)
        try:
            query = "SELECT last_notification_time FROM user_notifications WHERE user_id = %s LIMIT 1"
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()
            return (
                row["last_notification_time"]
                if row and "last_notification_time" in row
                else None
            )
        finally:
            cursor.close()
            conn.close()

    def set_last_notification_time(self, user_id: int, time: datetime) -> bool:
        conn = self.db.connect()
        cursor = conn.cursor(buffered=True)
        try:
            query = "UPDATE user_notifications SET last_notification_time = %s WHERE user_id = %s"
            cursor.execute(query, (time, user_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating last_notification_time: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def mark_articles_as_viewed(self, user_id: int, article_ids: List[int]) -> None:
        if not article_ids:
            return
        conn = self.db.connect()
        cursor = conn.cursor(buffered=True)
        try:
            viewed_at = datetime.now(timezone.utc)
            values = [(user_id, aid, viewed_at) for aid in article_ids]
            query = """
                INSERT IGNORE INTO viewed_articles (user_id, article_id, viewed_at)
                VALUES (%s, %s, %s)
            """
            cursor.executemany(query, values)
            conn.commit()
        finally:
            cursor.close()
            conn.close()
