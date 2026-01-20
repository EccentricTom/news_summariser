"""This module fetches news articles from an external API."""

import requests
import requests_cache
from dotenv import load_dotenv, find_dotenv
import os
import html
import unicodedata
import json
import re
import bs4

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

def extract_story(story:dict) -> dict:
    """Get news articles from news link and process"""
    news_link = story.get("news_link", "")
    if not news_link:
        return story
    response = requests.get(news_link)
    response.raise_for_status()
    story_html = response.content.decode("utf-8")
    story_soup = bs4.BeautifulSoup(story_html, features = "html.parser")
    story_soup = story_soup.find("article")
    if story_soup is None:
        return story
    try:
        article_byline_block = story_soup.find("div", attrs={"data-component": "byline-block"})
        article_byline_line = article_byline_block.find("span", attrs={"data-testid": "byline-new-contributors"})
        if article_byline_line is None:
            article_byline_line = article_byline_block.find("span", attrs={"data-testid": "byline-contributors"})
        article_byline = article_byline_line.get_text("[BREAK]", strip=True)
    except AttributeError:
        article_byline = "Unknown"
    story_body = story_soup.find_all("div", attrs= {"data-component": "text-block"})
    story_text: list[str] = []
    story_text = " \n\n ".join(block.get_text(" ", strip=True) for block in story_body)
    story["full_story"] = clean_story_body(story_text)
    if "[BREAK]" in article_byline:
        story["byline"] = article_byline.split("[BREAK]")[0]
        story["reporter_title"] = article_byline.split("[BREAK]")[1]
    else:
        story["byline"] = article_byline
        story["reporter_title"] = None
    return story

def clean_story_body(s:str) -> str:
    """Clean up the fetched story body for any remaining html elements."""
    # Decode HTML entities like &quot;, &amp;
    s = html.unescape(s)
    # Replace non-breaking spaces with regular spaces
    s = s.replace("\xa0", " ")
    # Normalize unicode (e.g., fancy quotes)
    s = unicodedata.normalize("NFKC", s)
    # Tidy whitespace
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def extract_all_stories(stories:list) -> list:
    return_list = []
    for story in stories:
        if story.get("title") is None:
            continue
        return_list.append(extract_story(story))
    return return_list


if __name__ == "__main__":
    all_news = fetch_news_all()
    print(all_news.keys())
    latest_news = get_news_by_category("Latest",cache=False)
    print(json.dumps(latest_news, indent=2))
    technology_news = get_news_by_category("Business", cache=False)
    technology_news = extract_all_stories(technology_news[:3])
    for news in technology_news:
        print("TITLE:")
        print(news.get("title"))
        print("")
        print("BYLINE")
        print(news.get("byline"))
        print("REPORTER TITLE")
        print(news.get('reporter_title'))
        print("")
        print(news.get("full_story"))
        print("")
        print("#"*30)


