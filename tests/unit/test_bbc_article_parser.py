from news_summariser.parsing.bbc_article_parser import clean_story_body, extract_story_from_html

def test_clean_story_body_normalizes():
    raw = 'Hello&nbsp;world &quot;test&quot;\n\n\nMore\xa0text\t\there'
    cleaned = clean_story_body(raw)
    assert 'Hello world "test"' in cleaned
    assert "\xa0" not in cleaned
    assert "\t" not in cleaned

def test_extract_story_from_html_parses_byline_and_text():
    story = {"title": "X", "news_link": "https://bbc.local/a"}

    html = """
    <article>
      <div data-component="byline-block">
        <span data-testid="byline-new-contributors">Jane Doe[BREAK]Reporter</span>
      </div>
      <div data-component="text-block">First paragraph.</div>
      <div data-component="text-block">Second paragraph.</div>
    </article>
    """

    out = extract_story_from_html(story, html)
    assert out["byline"] == "Jane Doe"
    assert out["reporter_title"] == "Reporter"
    assert "First paragraph." in out["full_story"]
