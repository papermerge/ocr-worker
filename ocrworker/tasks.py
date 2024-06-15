import logging
import mimetypes
import uuid
from pathlib import Path

from celery import chain, group, shared_task

from ocrworker import config, constants, db, plib, utils
from ocrworker.ocr import run_one_page_ocr

logger = logging.getLogger(__name__)
db_session = db.get_db()

settings = config.get_settings()

STARTED = "started"
COMPLETE = "complete"
PAGE_PDF = "page.pdf"


@shared_task()
def ocr_document_task(document_id, lang):
    logger.debug(f"Task started, document_id={document_id}, lang={lang}")

    with db_session() as session:
        doc_ver = db.get_last_version(session, doc_id=document_id)
        pages = db.get_pages(session, doc_ver_id=doc_ver.id)

    target_docver_uuid = uuid.uuid4()
    target_page_uuids = [uuid.uuid4() for _ in range(len(pages))]

    logger.debug(f"target_docver_uuid={target_docver_uuid}")
    logger.debug(f"target_page_uuids={target_page_uuids}")

    lang = lang.lower()

    doc_ver_path = plib.abs_docver_path(doc_ver.id, doc_ver.file_name)
    _type, encoding = mimetypes.guess_type(doc_ver_path)
    if _type is None:
        raise ValueError("Could not guess mimetype")

    if encoding not in ("application/pdf", "application/image"):
        raise ValueError(f"Unsupported format for document: {doc_ver_path}")

    per_page_ocr_tasks = [
        ocr_page_task.s(
            doc_id=doc_ver.id,
            doc_ver_id=doc_ver.id,
            page_number=index + 1,
            target_docver_id=target_docver_uuid,
            target_page_id=target_page_uuid,
            lang=lang,
            preview_width=300,
        )
        for index, target_page_uuid in enumerate(target_page_uuids)
    ]
    workflow = chain(
        group(per_page_ocr_tasks)
        | stitch_pages_task.s(
            doc_ver_id=doc_ver.id,
            target_docver_id=target_docver_uuid,
            target_page_ids=target_page_uuids,
        )
        | update_db_task.s(
            doc_id=document_id,
            doc_ver_id=doc_ver.id,
            target_docver_id=target_docver_uuid,
            target_page_ids=target_page_uuids,
        )
        | notify_index_task.s()
    )
    workflow.apply_async()


@shared_task()
def ocr_page_task(**kwargs):
    """OCR one single page"""
    doc_ver_id = kwargs["doc_ver_id"]
    target_page_id = kwargs["target_page_id"]
    lang = kwargs["lang"]
    page_number = kwargs["page_number"]
    preview_width = kwargs["preview_width"]

    with db_session() as session:
        doc_ver = db.get_doc_ver(session, doc_ver_id)

    sidecar_dir = Path(
        settings.papermerge__main__media_root, constants.OCR, constants.PAGES
    )

    output_dir = plib.abs_page_path(target_page_id)

    if not sidecar_dir.parent.exists():
        sidecar_dir.parent.mkdir(parents=True, exist_ok=True)

    run_one_page_ocr(
        file_path=doc_ver.file_path,
        output_dir=output_dir / PAGE_PDF,
        lang=lang,
        sidecar_dir=sidecar_dir,
        uuid=target_page_id,
        page_number=page_number,
        preview_width=preview_width,
    )

    return True


@shared_task()
def stitch_pages_task(_, **kwargs):
    logger.debug(f"Stitching pages for args={kwargs}")
    doc_ver_id = kwargs["doc_ver_id"]
    target_doc_ver_id = kwargs["target_doc_ver_id"]
    target_page_ids = kwargs["target_page_ids"]
    with db_session() as session:
        doc_ver = db.get_doc_ver(session, doc_ver_id)

    dst = plib.abs_docver_path(target_doc_ver_id, doc_ver.file_name)
    srcs = [
        plib.abs_page_path(page_id) / PAGE_PDF for page_id in target_page_ids
    ]
    utils.stitch_pdf(srcs=srcs, dst=dst)


@shared_task()
def update_db_task(_, **kwargs):
    logger.debug(f"Update DB doc_id={kwargs}")
    # create doc ver target version
    # add its pages (with extracted text)


@shared_task()
def notify_index_task(_, **kwargs):
    logger.debug(f"Update notify index doc_id={kwargs}")
