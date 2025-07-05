import pytest
from unittest.mock import patch, MagicMock
from server.repository import likes_dislikes_repository
from server.repository.likes_dislikes_repository import LikesDislikesRepository


@pytest.fixture
def repo():
    db = MagicMock()
    return LikesDislikesRepository(db)

def test_upsert_reaction_update(repo):
    repo._run_write = MagicMock(return_value=1)
    result = repo.upsert_reaction(1, 1, True)
    assert result == "updated"

def test_upsert_reaction_insert(repo):
    repo._run_write = MagicMock(side_effect=[0, 1])
    result = repo.upsert_reaction(1, 1, True)
    assert result == "created"

def test_delete_reaction_deleted(repo):
    repo._run_write = MagicMock(return_value=1)
    result = repo.delete_reaction(1, 1)
    assert result == "deleted"

def test_delete_reaction_not_found(repo):
    repo._run_write = MagicMock(return_value=0)
    result = repo.delete_reaction(1, 1)
    assert result == "not_found"

def test_remove_like(repo):
    repo._remove_specific_reaction = MagicMock(return_value='deleted')
    result = repo.remove_like(1, 1)
    assert result == 'deleted'

def test_remove_dislike(repo):
    repo._remove_specific_reaction = MagicMock(return_value='deleted')
    result = repo.remove_dislike(1, 1)
    assert result == 'deleted'

def test_get_user_reaction(repo):
    conn = repo.db.connect.return_value
    cursor = MagicMock()
    with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
        cursor.__enter__.return_value = cursor
        cursor.fetchone.return_value = [1]
        result = repo.get_user_reaction(1, 1)
        assert result is True

def test_get_reacted_articles(repo):
    repo._build_articles = MagicMock(return_value=[MagicMock()])
    conn = repo.db.connect.return_value
    cursor = MagicMock()
    with patch('server.utils.repository_helper.with_cursor', return_value=cursor):
        cursor.__enter__.return_value = cursor
        cursor.fetchall.return_value = [{}]
        result = repo.get_reacted_articles(1, True)
        assert isinstance(result, list)

def test_upsert_reaction_error(repo):
    repo._run_write = MagicMock(side_effect=Exception('fail'))
    result = repo.upsert_reaction(1, 1, True)
    assert result == 'error'

def test_delete_reaction_error(repo):
    repo._run_write = MagicMock(side_effect=Exception('fail'))
    result = repo.delete_reaction(1, 1)
    assert result == 'error' 