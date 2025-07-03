import pytest
from unittest.mock import patch, MagicMock
from server.repository import viewed_article_repository
from server.repository.viewed_article_repository import ViewedArticleRepository


@pytest.fixture
def repo():
    db = MagicMock()
    return ViewedArticleRepository(db)

def test_get_viewed_article_ids_by_user(repo):
    with patch.object(ViewedArticleRepository, 'get_viewed_article_ids_by_user', return_value=[1, 2]):
        result = repo.get_viewed_article_ids_by_user(1)
        assert result == [1, 2] 