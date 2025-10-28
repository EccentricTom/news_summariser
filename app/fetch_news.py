"""This module fetches news articles from an external API."""

import requests
import requests_cache
from dotenv import load_dotenv
import os
import html
import unicodedata
import json
import re
import bs4

load_dotenv()
requests_cache.install_cache('.cache/news_cache', expire_after=300)

API_URL = os.getenv("API_URL")
API_LANG = os.getenv("API_LANG")
print(f"API_URL: {API_URL}, API_LANG: {API_LANG}")

def fetch_news():
    """Fetch news articles from the external API."""
    response = requests.get(f"{API_URL}/news?lang={API_LANG}")
    response.raise_for_status()
    return response.json()

def fetch_news_cacheless():
    """Fetch news articles without using the cache."""
    with requests_cache.disabled():
        response = requests.get(f"{API_URL}/news?lang={API_LANG}")
        response.raise_for_status()
        return response.json()

def clear_news_cache():
    """Clear the news cache."""
    requests_cache.clear()

def get_news_by_category(category:str, cache:bool = True):
    """Get news articles by category, using cache if specified."""
    if cache:
        news = fetch_news()
    else:
        news = fetch_news_cacheless()
    return news.get(category, [])

def extract_story(story:dict) -> dict:
    """Get news articles from news link and process"""
    print(story)
    news_link = story.get("news_link", "")
    if not news_link:
        return story
    response = requests.get(news_link)
    response.raise_for_status()
    story_html = response.content.decode("utf-8")
    story_soup = bs4.BeautifulSoup(story_html)
    story_soup = story_soup.find("article")
    if story_soup is None:
        return story
    story_body = story_soup.find_all("div", attrs= {"data-component": "text-block"})
    story_text = []
    story_text = " \n\n ".join(block.get_text(" ", strip=True) for block in story_body)
    story["body"] = clean_story_body(story_text)
    return story

def clean_story_body(s:str) -> str:
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
    latest_news = get_news_by_category("Latest",cache=False)
    print(json.dumps(latest_news, indent=2))
    technology_news = get_news_by_category("Tech", cache=False)
    technology_news = extract_all_stories(technology_news[:3])
    for news in technology_news:
        print(news.get("title"))
        print("")
        print(news.get("body"))
        print("")


