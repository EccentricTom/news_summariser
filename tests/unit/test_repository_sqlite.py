from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from news_summariser.db.schema import Base, NewsTable
from news_summariser.db.repository import NewsRepository

def test_repository_inserts_rows():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine, future=True) as session:
        repo = NewsRepository(session)
        repo.insert_many([{
            "title": "T",
            "category": "Business",
            "summary": "S",
            "full_story": "F",
            "byline": "B",
            "reporter_title": "R",
        }])

        row = session.execute(select(NewsTable).where(NewsTable.title == "T")).scalar_one()
        assert row.category == "Business"
