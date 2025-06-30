import pytest
from server.external_apis.base_api import BaseNewsApiClient


def test_base_api_cannot_instantiate():
    print("\ntest_base_api_cannot_instantiate: Should raise TypeError")
    with pytest.raises(TypeError):
        BaseNewsApiClient()
    print("PASS: TypeError was correctly raised for abstract base class.")


def test_base_api_requires_fetch_top_headlines():
    print(
        "\ntest_base_api_requires_fetch_top_headlines: Should raise TypeError for missing method"
    )

    class IncompleteClient(BaseNewsApiClient):
        pass

    with pytest.raises(TypeError):
        IncompleteClient()
    print("PASS: TypeError was correctly raised for missing fetch_top_headlines.")


def test_base_api_subclass_works():
    print("\ntest_base_api_subclass_works: Should instantiate and call method")

    class DummyClient(BaseNewsApiClient):
        def fetch_top_headlines(self, category: str):
            return f"dummy for {category}"

    client = DummyClient()
    result = client.fetch_top_headlines("business")
    print("Result:", result)
    assert result == "dummy for business"
    print("PASS: DummyClient works as expected.")
