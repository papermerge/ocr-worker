from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    papermerge__redis__url: str | None = None
    papermerge__main__logging_cfg: Path | None = None
    papermerge__main__media_root: Path = Path(".")
    papermerge__main__prefix: str | None = None
    papermerge__database__url: str = "sqlite:////db/db.sqlite3"


@lru_cache()
def get_settings():
    return Settings()
