from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from ocrworker.config import get_settings


@lru_cache()
def get_engine(url: str | None = None):
    settings = get_settings()

    if url is None:
        SQLALCHEMY_DATABASE_URL = settings.papermerge__database__url
    else:
        SQLALCHEMY_DATABASE_URL = url

    connect_args = {}

    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        # sqlite specific connection args
        connect_args = {"check_same_thread": False}

    return create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args=connect_args,
        poolclass=NullPool,
    )
