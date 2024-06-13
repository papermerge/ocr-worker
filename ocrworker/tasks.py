import logging
import mimetypes
import uuid
from pathlib import Path
from uuid import UUID

import ocrmypdf
from celery import group, shared_task

from ocrworker import config, constants, db, models, plib

logger = logging.getLogger(__name__)
db_session = db.get_db()

logger = logging.getLogger(__name__)
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
        raise ValueError("Mimetype of the")

    if encoding not in ("application/pdf", "application/image"):
        raise ValueError(f"Unsupported format for document: {doc_ver_path}")

    tasks_list = [
        ocr_page_task.s(
            doc_ver, index + 1, target_docver_uuid, target_page_uuid, lang, 300
        )
        for index, target_page_uuid in enumerate(target_page_uuids)
    ]
    job = group(tasks_list)
    result = job.apply_async()
    result.join()


@shared_task(acks_late=True, reject_on_worker_lost=True)
def ocr_page_task(
    doc_ver: models.DocumentVersion,
    page_number: int,
    target_docver_uuid: UUID,
    target_page_uuid: UUID,
    lang: str,
    preview_width: int,
):
    sidecar_dir = Path(
        settings.papermerge__main__media_root, constants.OCR, constants.PAGES
    )

    output_dir = plib.abs_docver_path(target_docver_uuid, doc_ver.file_name)

    if not output_dir.parent.exists():
        output_dir.parent.mkdir(parents=True, exist_ok=True)

    ocrmypdf.ocr(
        doc_ver.file_path,
        output_dir,
        lang=lang,
        plugins=["ocrmypdf_papermerge.plugin"],
        progress_bar=False,
        output_type="pdf",
        pdf_renderer="hocr",
        use_threads=True,
        force_ocr=True,
        keep_temporary_files=False,
        sidecar_dir=sidecar_dir,
        uuids=target_page_uuid,
        pages=str(page_number),
        sidecar_format="svg",
        preview_width=preview_width,
        deskew=True,
    )

    return True
