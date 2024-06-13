import logging
import uuid

from celery import shared_task

from ocrworker import db, ocr

logger = logging.getLogger(__name__)
db_session = db.get_db()


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

    ocr.ocr_document(
        doc_ver=doc_ver,
        lang=lang,
        target_docver_uuid=target_docver_uuid,
        target_page_uuids=target_page_uuids,
    )

    logger.debug("Task complete")

    return document_id
