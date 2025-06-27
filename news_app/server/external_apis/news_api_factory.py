from server.external_apis.newsapi_org import NewsApiOrgClient
from server.external_apis.thenewsapi_com import TheNewsApiClient


def get_news_api_client(source_name: str):
    if source_name == "News API":
        return NewsApiOrgClient()
    elif source_name == "The News API":
        return TheNewsApiClient()
    else:
        raise ValueError(f"Unknown news API source: {source_name}")
