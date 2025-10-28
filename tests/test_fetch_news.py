"""Test the fetch_news module."""

import pytest
import requests_cache
from app import fetch_news

@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    """Clear the news cache before each test."""
    fetch_news.clear_news_cache()
    yield
    fetch_news.clear_news_cache()

def test_fetch_news_returns_data():
    """Test that fetch_news returns data from the API."""
    data = fetch_news.fetch_news()
    assert isinstance(data, dict)
    assert "Latest" in data

def test_get_latest_news_with_cache():
    """Test get_latest_news with cache enabled."""
    latest_news = fetch_news.get_latest_news(cache=True)
    assert isinstance(latest_news, list)

def test_get_latest_news_without_cache():
    """Test get_latest_news with cache disabled."""
    latest_news = fetch_news.get_latest_news(cache=False)
    assert isinstance(latest_news, list)

def test_get_news_by_category_with_cache():
    """Test get_news_by_category with cache enabled."""
    tech_news = fetch_news.get_news_by_category("Tech", cache=True)
    assert isinstance(tech_news, list)

def test_get_news_by_category_without_cache():
    """Test get_news_by_category with cache disabled."""
    tech_news = fetch_news.get_news_by_category("Tech", cache=False)
    assert isinstance(tech_news, list)

def test_cache_functionality():
    """Test that caching works as expected."""
    # First call should populate the cache
    fetch_news.get_latest_news(cache=True)
    assert requests_cache.get_cache().contains(url=f"{fetch_news.API_URL}/news?lang={fetch_news.API_LANG}")

    # Clear cache and ensure it's empty
    fetch_news.clear_news_cache()
    assert not requests_cache.get_cache().contains(url=f"{fetch_news.API_URL}/news?lang={fetch_news.API_LANG}")
