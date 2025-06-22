from typing import List, Optional
from server.models.category_model import Category
from server.repository.db_connector import DBConnector


class CategoryRepository:
    def __init__(self, db: DBConnector):
        self.db = db

    def get_all_categories(self, include_hidden: bool = False) -> List[Category]:
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM categories"
            if not include_hidden:
                query += " WHERE is_hidden = FALSE"
            query += " ORDER BY name"
            cursor.execute(query)
            rows = cursor.fetchall()
            return [Category(**row) for row in rows]
        finally:
            cursor.close()

    def get_category_by_name(self, name: str) -> Optional[Category]:
        name = name.strip().lower()
        conn = self.db.connect()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM categories WHERE LOWER(name) = %s", (name,))
            row = cursor.fetchone()
            return Category(**row) if row else None
        finally:
            cursor.close()

    def add_category(self, name: str) -> bool:
        try:
            name = name.strip().lower()
            conn = self.db.connect()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM categories WHERE LOWER(name) = %s", (name,))
            if cursor.fetchone():
                return False  # already exists

            cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
            conn.commit()
            return True
        except Exception as ex:
            print(f"Error adding category: {ex}")
            return False
        finally:
            cursor.close()

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
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as ex:
            print(f"Error deleting category: {ex}")
            return False
        finally:
            cursor.close()

    def set_category_hidden(self, category_id: int, is_hidden: bool) -> bool:
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categories SET is_hidden = %s WHERE id = %s",
                (is_hidden, category_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as ex:
            print(f"Error updating category hidden status: {ex}")
            return False
        finally:
            cursor.close()
