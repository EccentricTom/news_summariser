"""This module fetches news articles from an external API."""

import requests_cache
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables
load_dotenv(find_dotenv())

def _api_url() -> str:
    url = os.getenv("API_URL")
    if not url:
        raise RuntimeError("API_URL is not set")
    return url

def _api_lang() -> str:
    lang = os.getenv("API_LANG", "en")
    return lang

# create a cached session (test can monkeypatch this)
session = requests_cache.CachedSession(
    cache_name=".cache/news_cache",
    expire_after=600,
)

def fetch_news_all():
    resp = session.get(f"{_api_url()}/news?lang={_api_lang()}")
    resp.raise_for_status()
    return resp.json()

def fetch_news_all_cacheless():
    with session.cache_disabled():
        resp = session.get(f"{_api_url()}/news?lang={_api_lang()}")
        resp.raise_for_status()
        return resp.json()

def clear_news_cache():
    session.cache.clear()

def get_news_by_category(category:str, cache:bool = True) -> list:
    """Get news articles by category, using cache if specified."""
    if cache:
        news = fetch_news_all()
    else:
        news = fetch_news_all_cacheless()
    return news.get(category, [])
