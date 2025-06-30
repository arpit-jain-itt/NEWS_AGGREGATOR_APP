import pytest
from server.external_apis.news_api_factory import get_news_api_client
from server.external_apis.newsapi_org import NewsApiOrgClient
from server.external_apis.thenewsapi_com import TheNewsApiClient


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
