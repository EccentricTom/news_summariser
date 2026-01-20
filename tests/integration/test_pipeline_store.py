import pytest
import responses
import requests_cache
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from news_summariser.client.news_api_client import NewsApiClient
from news_summariser.db.schema import Base, NewsTable
from news_summariser.db.repository import NewsRepository
from news_summariser.parsing.bbc_article_parser import extract_all_stories


@pytest.mark.integration
@responses.activate
def test_ingest_pipeline_stores_parsed_and_summarised_story(tmp_path):
    # --- Arrange: fake API + fake BBC article page ---
    api_url = "https://fake-api.local"
    api_lang = "en"
    story_url = "https://bbc.local/article-1"

    responses.add(
        responses.GET,
        f"{api_url}/news?lang={api_lang}",
        json={
            "Business": [
                {"title": "Markets rally on earnings", "news_link": story_url}
            ]
        },
        status=200,
    )

    fake_article_html = """
    <html><body>
      <article>
        <div data-component="byline-block">
          <span data-testid="byline-new-contributors">Jane Doe[BREAK]Business reporter</span>
        </div>
        <div data-component="text-block">First paragraph.</div>
        <div data-component="text-block">Second paragraph.</div>
      </article>
    </body></html>
    """
    responses.add(
        responses.GET,
        story_url,
        body=fake_article_html,
        status=200,
        content_type="text/html",
    )

    # --- Arrange: single HTTP session used by BOTH client and parser ---
    http_session = requests_cache.CachedSession(
        str(tmp_path / "http_cache"),
        expire_after=300,
    )
    api = NewsApiClient(api_url=api_url, api_lang=api_lang, session=http_session)

    # --- Arrange: real DB (sqlite in-memory) ---
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    # --- Act: fetch -> parse -> summarise (stub) -> store ---
    stories = api.get_by_category("Business", cache=False)
    detailed = extract_all_stories(stories, session=http_session)

    class DummySummariser:
        def summarise(self, text: str, max_length: int = 200, min_length: int = 30) -> str:
            text = text or ""
            return "SUMMARY: " + text[:40]

    summariser = DummySummariser()

    for s in detailed:
        s["category"] = "Business"
        s["summary"] = summariser.summarise(s.get("full_story", ""), max_length=150, min_length=30)

    with Session(engine, future=True) as session:
        repo = NewsRepository(session)
        inserted = repo.insert_many(detailed)

        assert inserted == 1

        row = session.execute(
            select(NewsTable).where(NewsTable.title == "Markets rally on earnings")
        ).scalar_one()

        assert row.category == "Business"
        assert row.byline == "Jane Doe"
        assert row.reporter_title == "Business reporter"
        assert "First paragraph." in row.full_story
        assert row.summary.startswith("SUMMARY:")

    # Optional sanity: API call + article call happened
    assert len(responses.calls) == 2


