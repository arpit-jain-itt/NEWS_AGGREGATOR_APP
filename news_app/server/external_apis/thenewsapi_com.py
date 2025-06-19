import requests
from config.config import THE_NEWS_API_KEY, THE_NEWS_API_ENDPOINT
from .base_api import BaseNewsApiClient


class TheNewsApiClient(BaseNewsApiClient):
    def __init__(self):
        self.api_key = THE_NEWS_API_KEY
        self.endpoint = THE_NEWS_API_ENDPOINT

    def fetch_top_headlines(self, category: str = None):
        url = self.endpoint.format(api_key=self.api_key)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
        else:
            response.raise_for_status()
