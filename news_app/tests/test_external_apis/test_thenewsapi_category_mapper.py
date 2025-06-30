from server.external_apis.thenewsapi_category_mapper import map_article_to_category


def test_map_article_to_category_business():
    article = {"title": "Stock market surges", "description": "", "content": ""}
    category = map_article_to_category(article)
    print("\ntest_map_article_to_category_business:", category)
    assert category == "business"
    print("PASS: Correctly mapped to 'business'.")


def test_map_article_to_category_sports():
    article = {"title": "Football match results", "description": "", "content": ""}
    category = map_article_to_category(article)
    print("\ntest_map_article_to_category_sports:", category)
    assert category == "sports"
    print("PASS: Correctly mapped to 'sports'.")


def test_map_article_to_category_technology():
    article = {"title": "New AI software released", "description": "", "content": ""}
    category = map_article_to_category(article)
    print("\ntest_map_article_to_category_technology:", category)
    assert category == "technology"
    print("PASS: Correctly mapped to 'technology'.")


def test_map_article_to_category_default():
    article = {"title": "Random news", "description": "", "content": ""}
    category = map_article_to_category(article)
    print("\ntest_map_article_to_category_default:", category)
    assert category == "general"
    print("PASS: Correctly mapped to 'general' for unknown content.")
