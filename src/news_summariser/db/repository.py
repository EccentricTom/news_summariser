from typing import Iterable, Dict
from sqlalchemy.orm import Session

from .schema import NewsTable

class NewsRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert_many(self, news_data: Iterable[Dict]) -> int:
        """
        Inserts rows. Uses merge() so repeated titles update existing rows
        (nice for periodic ingestion).
        Returns number of processed items.
        """
        count = 0
        for story in news_data:
            title = story.get("title")
            if not title:  # skip invalid entries
                continue
            for key in ["category", "summary", "full_story"]:
                if key not in story or story[key] is None:
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
