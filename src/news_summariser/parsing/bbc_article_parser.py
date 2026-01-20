from typing import Optional
import html as html_lib
import unicodedata
import re
import bs4
import requests


def extract_story_from_html(story: dict, story_html: str) -> dict:
    """Parse BBC article HTML and enrich the story dict."""
    soup = bs4.BeautifulSoup(story_html, features="html.parser")
    article = soup.find("article")
    if article is None:
        return story
    try:
        byline_block = article.find("div", attrs={"data-component": "byline-block"})
        byline_line = byline_block.find("span", attrs={"data-testid": "byline-new-contributors"})
        if byline_line is None:
            byline_line = byline_block.find("span", attrs={"data-testid": "byline-contributors"})
        article_byline = byline_line.get_text("[BREAK]", strip=True)
    except AttributeError:
        article_byline = "Unknown"

    text_blocks = article.find_all("div", attrs={"data-component": "text-block"})
    story_text = " \n\n ".join(block.get_text(" ", strip=True) for block in text_blocks)

    story["full_story"] = clean_story_body(story_text)

    if "[BREAK]" in article_byline:
        story["byline"] = article_byline.split("[BREAK]")[0]
        story["reporter_title"] = article_byline.split("[BREAK]")[1]
    else:
        story["byline"] = article_byline
        story["reporter_title"] = None

    return story


def extract_story(story: dict, session: Optional[requests.Session] = None) -> dict:
    """Fetch article HTML via story['news_link'] and parse it."""
    news_link = story.get("news_link", "")
    if not news_link:
        return story

    sess = session or requests.Session()
    resp = sess.get(news_link)
    resp.raise_for_status()

    return extract_story_from_html(story, resp.text)


def clean_story_body(s: str) -> str:
    s = html_lib.unescape(s)
    s = s.replace("\xa0", " ")
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def extract_all_stories(stories: list[dict], session: Optional[requests.Session] = None) -> list[dict]:
    out = []
    for story in stories:
        if story.get("title") is None:
            continue
        out.append(extract_story(story, session=session))
    return out
