import requests
from config.config import NEWS_API_KEY, NEWS_API_ENDPOINT
from .base_api import BaseNewsApiClient


class NewsApiOrgClient(BaseNewsApiClient):
    def __init__(self):
        self.api_key = NEWS_API_KEY
        self.endpoint = NEWS_API_ENDPOINT

    def fetch_top_headlines(self, category: str):
        url = self.endpoint.format(category=category, api_key=self.api_key)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("articles", [])
        else:
            response.raise_for_status()
