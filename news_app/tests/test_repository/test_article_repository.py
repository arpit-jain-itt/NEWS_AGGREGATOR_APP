import pytest
from unittest.mock import MagicMock, patch
from server.repository.article_repository import ArticleRepository
from datetime import datetime

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

def test_get_latest_articles(repo):
    repo._query_articles = MagicMock(return_value=[MagicMock()])
    result = repo.get_latest_articles()
    assert isinstance(result, list)

def test_search_articles(repo):
    repo._query_articles = MagicMock(return_value=[MagicMock()])
    result = repo.search_articles(keyword='test')
    assert isinstance(result, list)

def test_is_article_saved_by_user_true(repo):
    conn = repo.db.connect.return_value
    cursor = MagicMock()
    with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
        cursor.__enter__.return_value = cursor
        cursor.fetchone.return_value = {'id': 1}
        result = repo.is_article_saved_by_user(1, 1)
        assert result is True

def test_save_article_for_user(repo):
    conn = repo.db.connect.return_value
    cursor = MagicMock()
    with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
        cursor.__enter__.return_value = cursor
        cursor.rowcount = 0
        conn.commit = MagicMock()
        result = repo.save_article_for_user(1, 1)
        assert result == 'already_saved'

def test_remove_saved_article(repo):
    conn = repo.db.connect.return_value
    cursor = MagicMock()
    with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
        cursor.__enter__.return_value = cursor
        cursor.rowcount = 1
        conn.commit = MagicMock()
        result = repo.remove_saved_article(1, 1)
        assert result == 'deleted'

def test_get_saved_articles_by_user(repo):
    repo._query_articles = MagicMock(return_value=[MagicMock()])
    result = repo.get_saved_articles_by_user(1)
    assert isinstance(result, list)

def test_get_headlines(repo):
    repo._query_articles = MagicMock(return_value=[MagicMock()])
    result = repo.get_headlines()
    assert isinstance(result, list)

def test_set_article_hidden(repo):
    conn = repo.db.connect.return_value
    cursor = MagicMock()
    with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
        cursor.__enter__.return_value = cursor
        cursor.rowcount = 0
        conn.commit = MagicMock()
        result = repo.set_article_hidden(1, True)
        assert result is False

def test_get_blocked_articles(repo):
    repo._query_articles = MagicMock(return_value=[MagicMock()])
    result = repo.get_blocked_articles()
    assert isinstance(result, list) 