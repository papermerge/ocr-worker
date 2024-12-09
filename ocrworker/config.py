from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    papermerge__redis__url: str | None = None
    papermerge__main__logging_cfg: Path | None = None
    papermerge__main__media_root: Path = Path(".")
    papermerge__main__prefix: str = ""
    papermerge__database__url: str = "sqlite:////db/db.sqlite3"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region_name: str | None = None
    papermerge__s3__bucket_name: str | None = None


@lru_cache()
def get_settings():
    return Settings()
