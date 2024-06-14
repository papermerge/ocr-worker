import logging
import mimetypes
import uuid
from pathlib import Path
from uuid import UUID

from celery import chain, group, shared_task

from ocrworker import config, constants, db, plib, utils
from ocrworker.ocr import run_ocr

logger = logging.getLogger(__name__)
db_session = db.get_db()

settings = config.get_settings()

STARTED = "started"
COMPLETE = "complete"


@shared_task(acks_late=True, reject_on_worker_lost=True)
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
            kwargs={
                "doc_id": doc_ver.id,
                "page_number": index + 1,
                "target_docver_id": target_docver_uuid,
                "target_page_id": target_page_uuid,
                "lang": lang,
                "preview_width": 300,
            }
        )
        for index, target_page_uuid in enumerate(target_page_uuids)
    ]
    workflow = chain(
        group(per_page_ocr_tasks)
        | stitch_pages_task.s()
        | update_db_task.s()
        | notify_index_task.s()
    )
    workflow.apply_async()


@shared_task(acks_late=True, reject_on_worker_lost=True)
def ocr_page_task(
    doc_ver_id: UUID,
    page_number: int,
    target_docver_id: UUID,
    target_page_id: UUID,
    lang: str,
    preview_width: int,
):
    with db_session() as session:
        doc_ver = db.get_doc_ver(session, doc_ver_id)

    sidecar_dir = Path(
        settings.papermerge__main__media_root, constants.OCR, constants.PAGES
    )

    output_dir = plib.abs_page_path(target_page_id)

    if not sidecar_dir.parent.exists():
        sidecar_dir.parent.mkdir(parents=True, exist_ok=True)

    run_ocr(
        file_path=doc_ver.file_path,
        output_dir=output_dir / "page.pdf",
        lang=lang,
        sidecar_dir=sidecar_dir,
        uuid=target_page_id,
        page_number=page_number,
        preview_width=preview_width,
    )

    return True


@shared_task()
def stitch_pages_task(args):
    logger.debug(f"Stitching pages for args={args}")
    document_id = args[0][0]
    doc_ver_id = args[0][2]
    with db_session() as session:
        doc_ver = db.get_doc_ver(session, doc_ver_id)

    doc_ver_path = plib.abs_docver_path(doc_ver_id, doc_ver.file_name)
    page_paths = [plib.abs_page_path(argset[3]) for argset in args]
    utils.stitch_pdf(src=page_paths, dst=doc_ver_path)

    return document_id


@shared_task()
def update_db_task(doc_id):
    logger.debug(f"Update DB doc_id={doc_id}")
    # create doc ver target version
    # add its pages (with extracted text)
    return doc_id


@shared_task()
def notify_index_task(doc_id):
    logger.debug(f"Update notify index doc_id={doc_id}")
    return doc_id
