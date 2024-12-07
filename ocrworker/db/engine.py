from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

from ocrworker.config import get_settings


settings = get_settings()


SQLALCHEMY_DATABASE_URL = settings.papermerge__database__url

connect_args = {}

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # sqlite specific connection args
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    poolclass=NullPool,
)

Session = sessionmaker(engine, expire_on_commit=False)


def get_engine() -> Engine:
    return engine
