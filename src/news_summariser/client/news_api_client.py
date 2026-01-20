from typing import Any, Dict, List, Optional
import requests_cache

class NewsApiClient:
    def __init__(self, api_url: str, api_lang: str, session: Optional[requests_cache.CachedSession] = None):
        self.api_url = api_url
        self.api_lang = api_lang
        self.session = session or requests_cache.CachedSession(".cache/news_cache", expire_after=300)

    def fetch_all(self, cache: bool = True) -> Dict[str, Any]:
        if cache:
            resp = self.session.get(f"{self.api_url}/news?lang={self.api_lang}")
        else:
            with self.session.cache_disabled():
                resp = self.session.get(f"{self.api_url}/news?lang={self.api_lang}")

        resp.raise_for_status()
        return resp.json()

    def get_by_category(self, category: str, cache: bool = True) -> List[dict]:
        return self.fetch_all(cache=cache).get(category, [])
