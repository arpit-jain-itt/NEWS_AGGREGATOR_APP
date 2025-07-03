import pytest
from unittest.mock import MagicMock, patch
from server.repository.category_repository import CategoryRepository

@pytest.fixture
def repo():
    db = MagicMock()
    return CategoryRepository(db)

def test_get_all_categories(repo):
    with patch('server.repository.category_repository.rows_to_models', return_value=[MagicMock()]):
        conn = repo.db.connect.return_value
        cursor = MagicMock()
        conn.close = MagicMock()
        with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
            cursor.__enter__.return_value = cursor
            cursor.fetchall.return_value = [{}]
            result = repo.get_all_categories()
            assert isinstance(result, list)

def test_get_category_by_name(repo):
    with patch('server.repository.category_repository.row_to_model', return_value=MagicMock()):
        conn = repo.db.connect.return_value
        cursor = MagicMock()
        conn.close = MagicMock()
        with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
            cursor.__enter__.return_value = cursor
            cursor.fetchone.return_value = {}
            result = repo.get_category_by_name('general')
            assert result is not None

# Example test for a method that fetches categories
# def test_get_all_categories():
#     with patch('server.repository.db_connector.get_db', return_value=MagicMock()):
#         result = category_repository.get_all_categories()
#         assert isinstance(result, list)

# Add more tests for other methods, mocking DB as needed. 