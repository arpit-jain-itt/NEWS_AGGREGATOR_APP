import pytest
from unittest.mock import patch, MagicMock
from server.repository import likes_dislikes_repository
from server.repository.likes_dislikes_repository import LikesDislikesRepository

# Example test for a method that fetches likes/dislikes
# def test_get_likes_dislikes():
#     with patch('server.repository.db_connector.get_db', return_value=MagicMock()):
#         result = likes_dislikes_repository.get_likes_dislikes()
#         assert isinstance(result, list)

# Add more tests for other methods, mocking DB as needed. 

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