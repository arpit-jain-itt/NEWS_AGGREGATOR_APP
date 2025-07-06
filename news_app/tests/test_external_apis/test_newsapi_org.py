import pytest
from unittest.mock import patch
from server.external_apis.newsapi_org import NewsApiOrgClient


def test_fetch_top_headlines_success():
    print("\ntest_fetch_top_headlines_success: Should return articles list")
    client = NewsApiOrgClient()
    fake_response = {"articles": [{"title": "Test News"}]}
    with patch("server.external_apis.newsapi_org.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = fake_response
        articles = client.fetch_top_headlines("business")
        print("Articles returned:", articles)
        assert articles == fake_response["articles"]
        print("Articles list returned as expected.")


def test_fetch_top_headlines_error():
    print("\ntest_fetch_top_headlines_error: Should raise Exception for non-200")
    client = NewsApiOrgClient()
    with patch("server.external_apis.newsapi_org.requests.get") as mock_get:
        mock_get.return_value.status_code = 500
        mock_get.return_value.raise_for_status.side_effect = Exception("API error")
        with pytest.raises(Exception):
            client.fetch_top_headlines("business")
        print("Exception was raised for non-200 response.")
