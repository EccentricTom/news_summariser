from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class NewsTable(Base):
    __tablename__ = "news"
    title = Column(String, primary_key=True, nullable=False)
    category = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    full_story = Column(String, nullable=False)
    byline = Column(String)
    reporter_title = Column(String)
