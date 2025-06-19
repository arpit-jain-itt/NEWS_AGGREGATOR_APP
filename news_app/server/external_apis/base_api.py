from abc import ABC, abstractmethod


class BaseNewsApiClient(ABC):
    @abstractmethod
    def fetch_top_headlines(self, category: str):

        pass
