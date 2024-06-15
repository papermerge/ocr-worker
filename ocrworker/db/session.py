from sqlalchemy.orm import sessionmaker
from .engine import get_engine


def get_db(url: str | None = None):
    Session = sessionmaker(get_engine(url))
    return Session
