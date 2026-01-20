import os
import pytest
from data import fetch_news

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_API") != "1",
    reason="Set RUN_LIVE_API=1 to run live API tests",
)

def test_live_api_responds():
    data = fetch_news.fetch_news_all_cacheless()
    assert isinstance(data, dict)
    assert len(data.keys()) > 0
