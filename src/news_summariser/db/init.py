from sqlalchemy.engine import Engine
from .schema import Base

def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine, checkfirst=True)
