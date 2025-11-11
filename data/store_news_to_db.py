from sqlalchemy import create_engine, MetaData, Table, Column, String, ARRAY
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base
from data import fetch_news
from dotenv import load_dotenv
import os

load_dotenv

DB_URL = os.getenv("DB_URL")
print(DB_URL)
Base = declarative_base()

class NewsTable(Base):
    __tablename__ = "News"
    title = Column(String, primary_key=True, nullable=False)
    category = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    full_story = Column(String, nullable=False)
    byline = Column(String)
    reporter_tile = Column(String)

def init_db_engine(DB_URL) -> Engine:
    engine = create_engine(DB_URL, echo=True,)
    return engine



if __name__ == "__main__":
    engine = init_db_engine(DB_URL)
    Base.metadata.create_all(engine)