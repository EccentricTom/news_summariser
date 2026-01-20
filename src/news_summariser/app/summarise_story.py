"""Summarise a news story text.

The news story must first be retrieved using the provided url."""

from data.fetch_news import get_news_by_category, extract_all_stories
from models.summarisation_model import SummarisationModel

def summarise_story(summariser: SummarisationModel, story:dict) -> str:
    """Summarise the news story at the given URL."""
    story_summary = summariser.summarise(story.get("body"), max_length=300, min_length=60)
    story["summary"] = story_summary
    return story

def summarise_n_stories(summariser: SummarisationModel, stories:list) -> list[str]:
    """Summarise multiple news stories given their URLs."""
    summaries = []
    for story in stories:
        summary = summarise_story(summariser, story)
        summaries.append(summary)
    return summaries


if __name__ == "__main__":
    summariser = SummarisationModel()
    tech_news = get_news_by_category("Tech", cache=False)
    tech_news = extract_all_stories(tech_news)
    if tech_news:
        tech_summaries = summarise_n_stories(summariser, tech_news[:5])
        print("\nSummaries of the first three Tech news stories:")
        for i, tech_summary in enumerate(tech_summaries, start=1):
            print(f"\nTech Story {i} Summary:")
            print(tech_summary.get("title"))
            print(tech_summary.get("summary"))
