from sqlalchemy.orm import sessionmaker
from .engine import engine


def get_db():
    Session = sessionmaker(engine)
    return Session
