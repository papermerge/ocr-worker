import uuid
import logging
import boto3

from pathlib import Path
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from ocrworker import config, plib
from ocrworker import constants as const

settings = config.get_settings()
logger = logging.getLogger(__name__)


def skip_if_s3_disabled(func):
    def inner(*args, **kwargs):
        if not is_enabled():
            logger.debug("S3 module is disabled")
            return

        return func(*args, **kwargs)

    return inner


def get_client() -> BaseClient:
    session = boto3.Session(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region_name,
    )
    client = session.client("s3")

    return client


def is_enabled():
    s3_settings = [
        settings.papermerge__s3__bucket_name,
        settings.aws_access_key_id,
        settings.aws_secret_access_key,
    ]
    logger.debug(s3_settings)
    return all(s3_settings)


def obj_exists(keyname: str) -> bool:
    client = get_client()
    try:
        client.head_object(Bucket=get_bucket_name(), Key=keyname)
    except ClientError:
        return False

    return True


@skip_if_s3_disabled
def download_docver(docver_id: uuid.UUID, file_name: str):
    """Downloads document version from S3"""
    doc_ver_path = plib.abs_docver_path(docver_id, file_name)
    keyname = Path(get_prefix()) / plib.docver_path(docver_id, file_name)
    if not doc_ver_path.exists():
        if not obj_exists(str(keyname)):
            # no local version + no s3 version
            raise ValueError(f"S3 key {keyname} not found")

    client = get_client()
    client.download_file(get_bucket_name(), keyname, str(doc_ver_path))


@skip_if_s3_disabled
def upload_file(rel_file_path: Path):
    """Uploads to S3 file specified by relative path

    Path is relative to `media root`.
    E.g. path "thumbnails/jpg/bd/f8/bdf862be/100.jpg", means that
    file absolute path on the file system is:
        <media root>/thumbnails/jpg/bd/f8/bdf862be/100.jpg

    The S3 keyname will then be:
        <prefix>/thumbnails/jpg/bd/f8/bdf862be/100.jpg
    """
    s3_client = get_client()
    keyname = get_prefix() / rel_file_path
    target: Path = plib.rel2abs(rel_file_path)

    if not target.exists():
        logger.error(f"Target {target} does not exist. Upload to S3 canceled.")
        return

    if not target.is_file():
        logger.error(f"Target {target} is not a file. Upload to S3 canceled.")
        return

    logger.debug(f"target={target} keyname={keyname}")

    s3_client.upload_file(
        str(target), Bucket=get_bucket_name(), Key=str(keyname)
    )


@skip_if_s3_disabled
def download_pages(target_page_ids: list[str]):
    """Downloads document pages from S3

    Will download only pages which are not found locally
    """
    to_download = []
    for page_id in target_page_ids:
        p = plib.abs_page_path(page_id) / const.PAGE_PDF
        if p.exists():
            logger.debug(f"{p} found locally")
        else:
            to_download.append(page_id)

    logger.debug(f"Queued for download from S3 {to_download}")


def get_bucket_name():
    return settings.papermerge__s3__bucket_name


def get_prefix():
    return settings.papermerge__main__prefix


def get_media_root():
    return settings.papermerge__main__media_root
