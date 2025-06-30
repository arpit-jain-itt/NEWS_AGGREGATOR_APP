import pytest
from unittest.mock import patch
from server.external_apis.news_api_factory import get_news_api_client
from server.external_apis.newsapi_org import NewsApiOrgClient
from server.external_apis.thenewsapi_com import TheNewsApiClient


def test_fetch_top_headlines_success():
    print("\ntest_fetch_top_headlines_success: Should return data list")
    client = TheNewsApiClient()
    fake_response = {"data": [{"title": "Test News"}]}
    with patch("server.external_apis.thenewsapi_com.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = fake_response
        articles = client.fetch_top_headlines("business")
        print("Articles returned:", articles)
        assert articles == fake_response["data"]
        print("PASS: Data list returned as expected.")


def test_fetch_top_headlines_error():
    print("\ntest_fetch_top_headlines_error: Should raise Exception for non-200")
    client = TheNewsApiClient()
    with patch("server.external_apis.thenewsapi_com.requests.get") as mock_get:
        mock_get.return_value.status_code = 500
        mock_get.return_value.raise_for_status.side_effect = Exception("API error")
        with pytest.raises(Exception):
            client.fetch_top_headlines("business")
        print("PASS: Exception was raised for non-200 response.")


def test_get_news_api_client_newsapi():
    print("\ntest_get_news_api_client_newsapi: Should return NewsApiOrgClient")
    client = get_news_api_client("News API")
    print("Client returned:", type(client).__name__)
    assert isinstance(client, NewsApiOrgClient)
    print("PASS: NewsApiOrgClient returned for 'News API'.")


def test_get_news_api_client_thenewsapi():
    print("\ntest_get_news_api_client_thenewsapi: Should return TheNewsApiClient")
    client = get_news_api_client("The News API")
    print("Client returned:", type(client).__name__)
    assert isinstance(client, TheNewsApiClient)
    print("PASS: TheNewsApiClient returned for 'The News API'.")


def test_get_news_api_client_invalid():
    print(
        "\ntest_get_news_api_client_invalid: Should raise ValueError for unknown source"
    )
    with pytest.raises(ValueError):
        get_news_api_client("Unknown API")
    print("PASS: ValueError raised for unknown source.")
