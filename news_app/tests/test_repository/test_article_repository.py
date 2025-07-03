import pytest
from unittest.mock import MagicMock, patch
from server.repository.article_repository import ArticleRepository

@pytest.fixture
def repo():
    db = MagicMock()
    return ArticleRepository(db)

def test_get_article_by_id(repo):
    repo._query_articles = MagicMock(return_value=[MagicMock()])
    result = repo.get_article_by_id(1)
    assert result is not None

def test_get_articles_by_category(repo):
    repo._query_articles = MagicMock(return_value=[MagicMock(), MagicMock()])
    result = repo.get_articles_by_category(1)
    assert len(result) == 2

def test_get_articles_by_ids_empty(repo):
    result = repo.get_articles_by_ids([])
    assert result == []

def test_get_next_article_id(repo):
    db = MagicMock()
    conn = db.connect.return_value
    cursor = conn.cursor.return_value
    cursor.fetchone.side_effect = [(5,), (4,)]
    repo = ArticleRepository(db)
    with patch.object(conn, 'commit'), patch.object(conn, 'close'), patch.object(cursor, 'close'):
        next_id = repo.get_next_article_id()
        assert next_id == 6 