import os
import pytest
from news_summariser.config import load_settings
from news_summariser.client.news_api_client import NewsApiClient

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_API") != "1",
    reason="Set RUN_LIVE_API=1 to run live API tests",
)

def test_live_api_responds():
    s = load_settings()
    api = NewsApiClient(s.api_url, s.api_lang)
    data = api.fetch_all(cache=False)
    assert isinstance(data, dict)
    assert len(data) > 0
