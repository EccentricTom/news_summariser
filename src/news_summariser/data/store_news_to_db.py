from sqlalchemy import create_engine, MetaData, Table, Column, String, ARRAY
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base
from data import fetch_news
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("DB_URL")
print(DB_URL)
Base = declarative_base()

class NewsTable(Base):
    __tablename__ = "news"
    title = Column(String, primary_key=True, nullable=False)
    category = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    full_story = Column(String, nullable=False)
    byline = Column(String)
    reporter_title = Column(String)

def init_db_engine(DB_URL) -> Engine:
    engine = create_engine(DB_URL, echo=True,)
    return engine

def create_table(engine: Engine) -> None:
    Base.metadata.create_all(engine)

def insert_news(engine: Engine, news_data: list[dict]) -> None:
    with engine.connect() as connection:
        for story in news_data:
            insert_stmt = NewsTable.__table__.insert().values(
                title=story.get("title", ""),
                category=story.get("category", ""),
                summary=story.get("summary", ""),
                full_story=story.get("full_story", ""),
                byline=story.get("byline", ""),
                reporter_title=story.get("reporter_title", "")
            )
            connection.execute(insert_stmt)
        connection.commit()


if __name__ == "__main__":
    engine = init_db_engine(DB_URL)
    create_table(engine)

    from data.fetch_news import get_news_by_category, extract_all_stories
    from models.summarisation_model import SummarisationModel
    summariser = SummarisationModel()
    categories = ["Technology", "Business", "entertainment"]
    all_news = []
    for category in categories:
        news_stories = get_news_by_category(category, cache=False)
        news_stories = extract_all_stories(news_stories)
        for detailed_story in news_stories[:2]:
            full_story = detailed_story.get("full_story", "")
            if full_story:
                summary = summariser.summarise(full_story, max_length=150, min_length=30)
                detailed_story["summary"] = summary
                detailed_story["category"] = category
            all_news.append(detailed_story)
    insert_news(engine, all_news)