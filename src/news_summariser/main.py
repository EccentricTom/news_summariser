from sqlalchemy.orm import Session

from news_summariser.config import load_settings
from news_summariser.db.engine import create_db_engine
from news_summariser.db.init import create_tables
from news_summariser.db.repository import NewsRepository
from news_summariser.models.summarisation_model import SummarisationModel
from news_summariser.data.fetch_news import get_news_by_category, extract_all_stories


def run_once():
    settings = load_settings()  # expects DB_URL etc.
    engine = create_db_engine(settings.db_url, echo=False)
    create_tables(engine)

    summariser = SummarisationModel()

    categories = ["Technology", "Business", "entertainment"]
    all_news = []

    for category in categories:
        news_stories = get_news_by_category(category, cache=False)
        detailed = extract_all_stories(news_stories)

        for story in detailed[:2]:
            full_story = story.get("full_story", "")
            if full_story:
                story["summary"] = summariser.summarise(full_story, max_length=150, min_length=30)
            story["category"] = category
            all_news.append(story)

    with Session(engine, future=True) as session:
        repo = NewsRepository(session)
        repo.insert_many(all_news)


if __name__ == "__main__":
    run_once()

