import importlib

import pytest
import responses
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from data import store_news_to_db


@pytest.mark.integration
@responses.activate
def test_fetch_extract_summarise_and_store(monkeypatch, tmp_path):
    # --- Arrange env (IMPORTANT: fetch_news reads env at import-time) ---
    api_url = "https://fake-api.local"
    monkeypatch.setenv("API_URL", api_url)
    monkeypatch.setenv("API_LANG", "en")

    from data import fetch_news as fetch_news_mod
    importlib.reload(fetch_news_mod)

    # --- Arrange fake API response ---
    story_link = "https://bbc.local/article-1"
    responses.add(
        responses.GET,
        f"{api_url}/news?lang=en",
        json={
            "Business": [
                {"title": "Markets rally on earnings", "news_link": story_link}
            ]
        },
        status=200,
    )

    # --- Arrange fake BBC-like HTML for extract_story ---
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
        story_link,
        body=fake_article_html,
        status=200,
        content_type="text/html",
    )

    # --- Arrange DB (real engine, fast) ---
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite+pysqlite:///{db_path}", future=True)

    store_news_to_db.create_table(engine)

    # --- Stub summariser (don’t download HF model in tests) ---
    class DummySummariser:
        def summarise(self, text: str, max_length=150, min_length=30) -> str:
            return "SUMMARY: " + (text[:50] if text else "")

    summariser = DummySummariser()

    # --- Act: run the pipeline steps you have today ---
    stories = fetch_news_mod.get_news_by_category("Business", cache=False)
    detailed = fetch_news_mod.extract_all_stories(stories)

    # enrich for DB insert
    for s in detailed:
        s["category"] = "Business"
        s["summary"] = summariser.summarise(s.get("full_story", ""))

        # store_news_to_db currently expects reporter_tile (typo)
        # If you fix it to reporter_title, update this line.
        s["reporter_tile"] = s.get("reporter_title")

    store_news_to_db.insert_news(engine, detailed)

    # --- Assert: row exists and fields populated ---
    with Session(engine) as session:
        row = session.execute(
            select(store_news_to_db.NewsTable).where(
                store_news_to_db.NewsTable.title == "Markets rally on earnings"
            )
        ).scalar_one()

        assert row.category == "Business"
        assert row.byline == "Jane Doe"
        assert "First paragraph." in row.full_story
        assert row.summary.startswith("SUMMARY:")
