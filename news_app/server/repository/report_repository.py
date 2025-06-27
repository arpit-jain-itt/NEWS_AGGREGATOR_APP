from typing import List, Optional
from server.models.report_model import Report
from server.utils.repository_helper import (
    with_cursor,
    rows_to_models,
    safe_execute,
)


class ReportRepository:
    def __init__(self, db):
        self.db = db

    def add_report(self, report: Report) -> bool:
        query = """
            INSERT INTO reports (user_id, article_id, reason, status)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE reason=VALUES(reason), created_at=NOW(), status='pending'
        """

        def do_add():
            conn = self.db.connect()
            try:
                with with_cursor(conn) as cursor:
                    cursor.execute(
                        query,
                        (
                            report.user_id,
                            report.article_id,
                            report.reason,
                            report.status,
                        ),
                    )
                    conn.commit()
                    return True
            finally:
                conn.close()

        return safe_execute(do_add, default=False)

    def get_report_count(self, article_id: int) -> int:
        query = "SELECT COUNT(*) FROM reports WHERE article_id = %s"
        conn = self.db.connect()
        try:
            with with_cursor(conn) as cursor:
                cursor.execute(query, (article_id,))
                (count,) = cursor.fetchone()
            return count
        finally:
            conn.close()

    def get_reported_articles(self) -> List[dict]:
        query = """
            SELECT article_id, COUNT(*) as report_count
            FROM reports
            GROUP BY article_id
            ORDER BY report_count DESC
        """
        conn = self.db.connect()
        try:
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        finally:
            conn.close()

    def get_reports_for_article(self, article_id: int) -> List[Report]:
        query = "SELECT * FROM reports WHERE article_id = %s"
        conn = self.db.connect()
        try:
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, (article_id,))
                rows = cursor.fetchall()
            return rows_to_models(rows, Report)
        finally:
            conn.close()

    def update_report_status(self, article_id: int, status: str):
        query = "UPDATE reports SET status = %s WHERE article_id = %s"
        conn = self.db.connect()
        try:
            with with_cursor(conn) as cursor:
                cursor.execute(query, (status, article_id))
                conn.commit()
        finally:
            conn.close()

    def get_reports_by_user(self, user_id: int) -> List[Report]:
        query = "SELECT * FROM reports WHERE user_id = %s"
        conn = self.db.connect()
        try:
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, (user_id,))
                rows = cursor.fetchall()
            return rows_to_models(rows, Report)
        finally:
            conn.close()

    def remove_report(self, user_id: int, article_id: int) -> bool:
        query = "DELETE FROM reports WHERE user_id = %s AND article_id = %s"

        def do_remove():
            conn = self.db.connect()
            try:
                with with_cursor(conn) as cursor:
                    cursor.execute(query, (user_id, article_id))
                    rowcount = cursor.rowcount
                    conn.commit()
                    return rowcount > 0
            finally:
                conn.close()

        return safe_execute(do_remove, default=False)
