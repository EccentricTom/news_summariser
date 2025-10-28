"""Summarise a news story text.

The news story must first be retrieved using the provided url."""

import requests
from app.fetch_news import fetch_news, get_latest_news, get_news_by_category, fetch_news_cacheless
import bs4
import transformers
from models.summarisation_model import SummarisationModel

def summarise_story(summariser: SummarisationModel, url:str) -> str:
    """Summarise the news story at the given URL."""
    response = requests.get(url)
    response.raise_for_status()
    story_text = response.content.decode('utf-8')
    story_soup = bs4.BeautifulSoup(story_text)
    story_body = story_soup.find_all("p")
    story_text = " ".join([p.get_text() for p in story_body])
    story_headline = story_soup.find("h1")
    if story_headline:
        story_headline = story_headline.get_text()
    return_dict = {"headline": story_headline, "summary": summariser.summarise(story_text, max_length=300, min_length=50)}
    return return_dict

def summarise_n_stories(summariser: SummarisationModel, stories:list) -> list[str]:
    """Summarise multiple news stories given their URLs."""
    summaries = []
    for story in stories:
        url = story.get("news_link", None)
        if not url:
            continue
        summary = summarise_story(summariser, url)
        summaries.append(summary)
    return summaries
    

if __name__ == "__main__":
    summariser = SummarisationModel()
    latest_news = get_latest_news(cache=False)
    if latest_news:
        first_story_url = "https://www.bbc.com/news/articles/c8drem8518do"
        print(f"Fetching and summarising story from URL: {first_story_url}")
        if first_story_url:
            summary = summarise_story(summariser, first_story_url)
            print("Summary of the first latest news story:")
            print(summary.get("headline"))
            print(summary.get("summary"))
        else:
            print("No URL found for the first latest news story.")
    else:
        print("No latest news stories found.")

    tech_news = get_news_by_category("Tech", cache=False)
    if tech_news:
        tech_summaries = summarise_n_stories(summariser, tech_news[:5])
        print("\nSummaries of the first three Tech news stories:")
        for i, tech_summary in enumerate(tech_summaries, start=1):
            print(f"\nTech Story {i} Summary:")
            print(tech_summary.get("headline"))
            print(tech_summary.get("summary"))