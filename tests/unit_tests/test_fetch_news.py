"""Test the fetch_news module."""

import pytest
import responses

from data import fetch_news

# Fixture to ensure tests use in-memory cache
@pytest.fixture(autouse=True)
def use_memory_cache(monkeypatch):
    """
    Ensure tests don't write to disk and start with an empty cache.
    """
    # Clear any existing cache
    fetch_news.clear_news_cache()

    yield

    fetch_news.clear_news_cache()

# Fixture to create a fake API endpoint so tests run reliably
@pytest.fixture
def api_env(monkeypatch):
    monkeypatch.setenv("API_URL", "https://fake-api.local")
    monkeypatch.setenv("API_LANG", "en")

@responses.activate
def test_fetch_news_returns_data(api_env):
    responses.add(
        responses.GET,
        "https://fake-api.local/news?lang=en",
        json={"Business": [{"title": "A", "news_link": "https://bbc.local/a"}]},
        status=200,
    )

    data = fetch_news.fetch_news_all()
    assert isinstance(data, dict)
    assert "Business" in data

@responses.activate
def test_get_news_by_category_existing(api_env):
    responses.add(
        responses.GET,
        "https://fake-api.local/news?lang=en",
        json={"Tech": [{"title": "T1"}]},
        status=200,
    )

    tech_news = fetch_news.get_news_by_category("Tech", cache=True)
    assert tech_news == [{"title": "T1"}]


@responses.activate
def test_get_news_by_category_missing_returns_empty_list(api_env):
    responses.add(
        responses.GET,
        "https://fake-api.local/news?lang=en",
        json={"Business": []},
        status=200,
    )

    missing = fetch_news.get_news_by_category("Tech", cache=True)
    assert missing == []


@responses.activate
def test_fetch_news_raises_for_non_200(api_env):
    responses.add(
        responses.GET,
        "https://fake-api.local/news?lang=en",
        json={"error": "nope"},
        status=500,
    )

    with pytest.raises(Exception):
        fetch_news.fetch_news_all()


@responses.activate
def test_cache_hits_network_once(api_env):
    # Same URL, same mocked response
    responses.add(
        responses.GET,
        "https://fake-api.local/news?lang=en",
        json={"Business": [{"title": "A"}]},
        status=200,
    )

    fetch_news.fetch_news_all()
    fetch_news.fetch_news_all()

    # If caching is working, only the first request should hit the mocked HTTP layer
    assert len(responses.calls) == 1


@responses.activate
def test_cacheless_always_hits_network(api_env):
    # Provide two responses in sequence for the same URL
    responses.add(
        responses.GET,
        "https://fake-api.local/news?lang=en",
        json={"Business": [{"title": "A"}]},
        status=200,
    )
    responses.add(
        responses.GET,
        "https://fake-api.local/news?lang=en",
        json={"Business": [{"title": "B"}]},
        status=200,
    )

    a = fetch_news.fetch_news_all()
    b = fetch_news.fetch_news_all_cacheless()

    assert a["Business"][0]["title"] == "A"
    assert b["Business"][0]["title"] == "B"
    assert len(responses.calls) == 2


def test_clean_story_body_normalizes_text():
    raw = 'Hello&nbsp;world &quot;test&quot;\n\n\nMore\xa0text\t\there'
    cleaned = fetch_news.clean_story_body(raw)
    assert 'Hello world "test"' in cleaned
    assert "\n\n" in cleaned
    assert "\xa0" not in cleaned
    assert "\t" not in cleaned


@responses.activate
def test_extract_story_no_news_link_returns_unchanged():
    story = {"title": "X"}
    out = fetch_news.extract_story(story.copy())
    assert out == story


@responses.activate
def test_extract_story_parses_byline_and_text(api_env):
    url = "https://bbc.local/article-1"
    story = {"title": "X", "news_link": url}

    html = """
    <html><body>
      <article>
        <div data-component="byline-block">
          <span data-testid="byline-new-contributors">Jane Doe[BREAK]Reporter</span>
        </div>
        <div data-component="text-block">First paragraph.</div>
        <div data-component="text-block">Second paragraph.</div>
      </article>
    </body></html>
    """
    responses.add(responses.GET, url, body=html, status=200)

    out = fetch_news.extract_story(story)
    assert out["byline"] == "Jane Doe"
    assert out["reporter_title"] == "Reporter"
    assert "First paragraph." in out["full_story"]
    assert "Second paragraph." in out["full_story"]


@responses.activate
def test_extract_story_missing_article_returns_original(api_env):
    url = "https://bbc.local/article-2"
    story = {"title": "X", "news_link": url}

    html = "<html><body><div>No article here</div></body></html>"
    responses.add(responses.GET, url, body=html, status=200)

    out = fetch_news.extract_story(story.copy())
    # Should not crash; should return story unchanged (no full_story/byline)
    assert out.get("full_story") is None
    assert out.get("byline") is None


def test_extract_all_stories_skips_missing_title(monkeypatch):
    stories = [{"title": None}, {"title": "OK", "news_link": ""}]
    out = fetch_news.extract_all_stories(stories)
    assert len(out) == 1
    assert out[0]["title"] == "OK"
