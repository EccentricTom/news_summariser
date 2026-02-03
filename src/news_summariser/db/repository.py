from typing import Iterable, Dict
from sqlalchemy.orm import Session

from .schema import NewsTable

class NewsRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert_many(self, news_data: Iterable[Dict]) -> int:
        count = 0
        for story in news_data:
            title = story.get("title")
            if not title:
                continue

            required = ("category", "summary", "full_story")
            if any(story.get(k) is None for k in required):
                continue

            row = NewsTable(
                title=title,
                category=story.get("category"),
                summary=story.get("summary"),
                full_story=story.get("full_story"),
                byline=story.get("byline"),
                reporter_title=story.get("reporter_title"),
            )
            self.session.merge(row)
            count += 1

        self.session.commit()
        return count

