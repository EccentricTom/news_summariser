"""This module fetches news articles from an external API."""

import requests
import requests_cache
from dotenv import load_dotenv
import os
import json

load_dotenv()
requests_cache.install_cache('.cache/news_cache', expire_after=300)

API_URL = os.getenv("API_URL")
API_LANG = os.getenv("API_LANG")
print(f"API_URL: {API_URL}, API_LANG: {API_LANG}")

def fetch_news():
    """Fetch news articles from the external API."""
    response = requests.get(f"{API_URL}/news?lang={API_LANG}")
    response.raise_for_status()
    return response.json()

def fetch_news_cacheless():
    """Fetch news articles without using the cache."""
    with requests_cache.disabled():
        response = requests.get(f"{API_URL}/news?lang={API_LANG}")
        response.raise_for_status()
        return response.json()
    
def clear_news_cache():
    """Clear the news cache."""
    requests_cache.clear()

def get_latest_news(cache:bool = True):
    """Get the latest news articles, using cache if specified."""
    if cache:
        news = fetch_news()
    else:
        news = fetch_news_cacheless()
    return news.get("Latest", [])

def get_news_by_category(category:str, cache:bool = True):
    """Get news articles by category, using cache if specified."""
    if cache:
        news = fetch_news()
    else:
        news = fetch_news_cacheless()
    return news.get(category, [])


if __name__ == "__main__":
    latest_news = get_latest_news(cache=False)
    print(json.dumps(latest_news, indent=2))
    technology_news = get_news_by_category("Tech", cache=False)
    print(json.dumps(technology_news, indent=2))

