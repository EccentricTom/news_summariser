"""
This module runs a full pipeline of pulling news articles, summarising and running sentiment analysis on them,
and then stores them in the database.
"""

from sqlalchemy.orm import Session
from typing import Optional
from news_summariser.config import load_settings
from news_summariser.client.news_api_client import NewsApiClient
from news_summariser.db.engine import create_db_engine
from news_summariser.db.init import create_tables
from news_summariser.db.repository import NewsRepository
from news_summariser.models.summarisation_model import SummarisationModel
from news_summariser.models.sentiment_model import SentimentModel
from news_summariser.parsing.bbc_article_parser import extract_all_stories

def pipeline(story_limit: Optional[int] = None):
    """
    Run the full news ingestion, summarisation, sentiment analysis, and storage pipeline.

    Args:
        story_limit (Optional[int]): If provided, limits the number of stories processed per category.
    """
    if story_limit is not None and story_limit <= 0:
        raise ValueError("story_limit must be a positive integer or None")
    settings = load_settings()
    engine = create_db_engine(settings.db_url, echo=False)
    create_tables(engine)

    api = NewsApiClient(settings.api_url, settings.api_lang)
    summariser = SummarisationModel()
    sentiment_analyser = SentimentModel()

    categories = ["Technology", "Business", "Entertainment"]
    all_news = []

    for category in categories:
        stories = api.get_by_category(category, cache=False)
        detailed = extract_all_stories(stories)  # uses requests.Session() internally unless you inject one
        if story_limit is not None:
            detailed = detailed[:story_limit]
        for story in detailed:
            full_story = story.get("full_story", "")
            if full_story:
                story["summary"] = summariser.summarise(full_story, max_length=150, min_length=30)
                #story["sentiment"] = sentiment_analyser.get_sentiment(full_story)
            story["category"] = category
            all_news.append(story)

    with Session(engine, future=True) as session:
        repo = NewsRepository(session)
        repo.insert_many(all_news)
