import responses
import requests_cache

from news_summariser.client.news_api_client import NewsApiClient

@responses.activate
def test_get_by_category_returns_list(tmp_path):
    session = requests_cache.CachedSession(str(tmp_path / "cache"), expire_after=300)
    api = NewsApiClient(api_url="https://fake-api.local", api_lang="en", session=session)

    responses.add(
        responses.GET,
        "https://fake-api.local/news?lang=en",
        json={"Business": [{"title": "A"}]},
        status=200,
    )

    out = api.get_by_category("Business", cache=True)
    assert out == [{"title": "A"}]

@responses.activate
def test_cache_hits_network_once(tmp_path):
    session = requests_cache.CachedSession(str(tmp_path / "cache"), expire_after=300)
    api = NewsApiClient(api_url="https://fake-api.local", api_lang="en", session=session)

    responses.add(
        responses.GET,
        "https://fake-api.local/news?lang=en",
        json={"Business": [{"title": "A"}]},
        status=200,
    )

    api.fetch_all(cache=True)
    api.fetch_all(cache=True)

    assert len(responses.calls) == 1
