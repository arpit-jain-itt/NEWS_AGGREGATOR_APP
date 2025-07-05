import pytest
from unittest.mock import MagicMock, patch
from server.repository.keyword_filter_repository import KeywordFilterRepository

@pytest.fixture
def repo():
    db = MagicMock()
    return KeywordFilterRepository(db)

def test_get_all_keywords(repo):
    with patch('server.utils.repository_helper.rows_to_models', return_value=[MagicMock()]):
        conn = repo.db.connect.return_value
        cursor = MagicMock()
        conn.close = MagicMock()
        with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
            cursor.__enter__.return_value = cursor
            cursor.fetchall.return_value = [{}]
            result = repo.get_all_keywords()
            assert isinstance(result, list)

def test_add_keyword(repo):
    with patch('server.utils.repository_helper.safe_execute', return_value=True):
        assert repo.add_keyword('test') is True
