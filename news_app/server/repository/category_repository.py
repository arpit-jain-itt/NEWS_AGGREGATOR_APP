from typing import List, Optional
from server.models.category_model import Category
from server.repository.db_connector import DBConnector
from server.utils.repository_helper import (
    with_cursor,
    rows_to_models,
    row_to_model,
    safe_execute,
)


class CategoryRepository:
    def __init__(self, db: DBConnector):
        self.db = db

    def get_all_categories(self, include_hidden: bool = False) -> List[Category]:
        conn = self.db.connect()
        try:
            query = "SELECT * FROM categories"
            if not include_hidden:
                query += " WHERE is_hidden = FALSE"
            query += " ORDER BY name"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            return rows_to_models(rows, Category)
        finally:
            conn.close()

    def get_category_by_name(self, name: str) -> Optional[Category]:
        name = name.strip().lower()
        conn = self.db.connect()
        try:
            query = "SELECT * FROM categories WHERE LOWER(name) = %s"
            with with_cursor(conn, dictionary=True) as cursor:
                cursor.execute(query, (name,))
                row = cursor.fetchone()
            return row_to_model(row, Category)
        finally:
            conn.close()

    def add_category(self, name: str) -> bool:
        def do_add():
            name_lc = name.strip().lower()
            conn = self.db.connect()
            try:
                with with_cursor(conn) as cursor:
                    cursor.execute(
                        "SELECT id FROM categories WHERE LOWER(name) = %s", (name_lc,)
                    )
                    if cursor.fetchone():
                        return False  # already exists
                    cursor.execute(
                        "INSERT INTO categories (name) VALUES (%s)", (name_lc,)
                    )
                    conn.commit()
                    return True
            finally:
                conn.close()

        return safe_execute(do_add, default=False)

    def get_or_create_category(self, name: str) -> Optional[Category]:
        cat = self.get_category_by_name(name)
        if cat:
            return cat
        if self.add_category(name):
            return self.get_category_by_name(name)
        return None

    def get_general_category(self) -> Category:
        cat = self.get_or_create_category("general")
        if cat is None:
            raise RuntimeError("Unable to obtain or create 'general' category")
        return cat

    def delete_category_by_id(self, category_id: int) -> bool:
        def do_delete():
            conn = self.db.connect()
            try:
                with with_cursor(conn) as cursor:
                    cursor.execute(
                        "DELETE FROM categories WHERE id = %s", (category_id,)
                    )
                    conn.commit()
                    return cursor.rowcount > 0
            finally:
                conn.close()

        return safe_execute(do_delete, default=False)

    def set_category_hidden(self, category_id: int, is_hidden: bool) -> bool:
        def do_update():
            conn = self.db.connect()
            try:
                with with_cursor(conn) as cursor:
                    cursor.execute(
                        "UPDATE categories SET is_hidden = %s WHERE id = %s",
                        (is_hidden, category_id),
                    )
                    conn.commit()
                    return cursor.rowcount > 0
            finally:
                conn.close()

        return safe_execute(do_update, default=False)
