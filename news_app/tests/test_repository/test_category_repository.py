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

def test_add_category_duplicate(repo):
    with patch('server.utils.repository_helper.with_cursor') as mock_cursor, \
         patch('server.utils.repository_helper.safe_execute', side_effect=lambda f, default=None: f()):
        cursor = MagicMock()
        mock_cursor.return_value = cursor
        cursor.__enter__.return_value = cursor
        cursor.fetchone.side_effect = [True]
        result = repo.add_category('dup')
        assert result is False

def test_get_or_create_category_exists(repo):
    repo.get_category_by_name = MagicMock(return_value=MagicMock())
    result = repo.get_or_create_category('exists')
    assert result is not None

def test_get_or_create_category_new(repo):
    repo.get_category_by_name = MagicMock(return_value=None)
    repo.add_category = MagicMock(return_value=True)
    repo.get_category_by_name = MagicMock(return_value=MagicMock())
    result = repo.get_or_create_category('new')
    assert result is not None

def test_get_general_category(repo):
    repo.get_or_create_category = MagicMock(return_value=MagicMock())
    result = repo.get_general_category()
    assert result is not None

def test_get_general_category_fail(repo):
    repo.get_or_create_category = MagicMock(return_value=None)
    with pytest.raises(RuntimeError):
        repo.get_general_category()

def test_set_category_hidden_fail(repo):
    with patch('server.utils.repository_helper.with_cursor') as mock_cursor, \
         patch('server.utils.repository_helper.safe_execute', side_effect=lambda f, default=None: f()):
        cursor = MagicMock()
        mock_cursor.return_value = cursor
        cursor.__enter__.return_value = cursor
        cursor.rowcount = 0
        cursor.commit = MagicMock()
        result = repo.set_category_hidden(1, True)
        assert result is False
