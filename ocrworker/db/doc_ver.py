import io
from uuid import UUID

from sqlalchemy import exc, select
from sqlalchemy.orm import Session

from ocrworker import models
from ocrworker.db.models import Document, DocumentVersion, Page


def get_doc(db_session: Session, doc_id: UUID) -> models.Document:
    with db_session as session:  # noqa
        stmt = select(Document).where(Document.id == doc_id)
        db_doc = session.scalars(stmt).one()
        model_doc = models.Document.model_validate(db_doc)

    return model_doc


def get_docs(db_session: Session, doc_ids: list[UUID]) -> list[models.Document]:
    with db_session as session:  # noqa
        stmt = select(Document).where(Document.id.in_(doc_ids))
        db_docs = session.scalars(stmt).all()
        model_docs = [
            models.Document.model_validate(db_doc) for db_doc in db_docs
        ]

    return model_docs


def get_last_version(
    db_session: Session, doc_id: UUID
) -> models.DocumentVersion:
    """
    Returns last version of the document
    identified by doc_id
    """
    with db_session as session:  # noqa
        stmt = (
            select(DocumentVersion)
            .join(Document)
            .where(
                DocumentVersion.document_id == doc_id,
            )
            .order_by(DocumentVersion.number.desc())
            .limit(1)
        )
        db_doc_ver = session.scalars(stmt).one()
        model_doc_ver = models.DocumentVersion.model_validate(db_doc_ver)

    return model_doc_ver


def get_doc_ver(
    db_session: Session, id: UUID  # noqa
) -> models.DocumentVersion:
    """
    Returns last version of the document
    identified by doc_id
    """
    with db_session as session:  # noqa
        stmt = select(DocumentVersion).where(DocumentVersion.id == id)
        db_doc_ver = session.scalars(stmt).one()
        model_doc_ver = models.DocumentVersion.model_validate(db_doc_ver)

    return model_doc_ver


def get_pages(db_session: Session, doc_ver_id: UUID) -> list[models.Page]:
    """
    Returns first page of the document version
    identified by doc_ver_id
    """
    result = []
    with db_session as session:  # noqa
        stmt = (
            select(Page)
            .where(
                Page.document_version_id == doc_ver_id,
            )
            .order_by(Page.number.asc())
        )
        try:
            db_pages = session.scalars(stmt).all()
        except exc.NoResultFound:
            session.close()
            raise Exception(
                f"DocVerID={doc_ver_id} does not have pages(s)."
                " Maybe it does not have associated file yet?"
            )
        result = [models.Page.model_validate(db_page) for db_page in db_pages]

    return list(result)


def get_page(
    db_session: Session,
    id: UUID,
) -> models.Page:
    with db_session as session:
        stmt = (
            select(Page)
            .join(DocumentVersion)
            .join(Document)
            .where(
                Page.id == id,
            )
        )
        try:
            db_page = session.scalars(stmt).one()
        except exc.NoResultFound:
            session.close()
            raise Exception(f"PageID={id} not found")
        result = models.Page.model_validate(db_page)

    return result


def increment_doc_ver(
    db_session: Session,
    document_id: UUID,
    target_docver_uuid: UUID,
    target_page_uuids: list[UUID],
    lang: str,
):
    doc_ver = get_last_version(db_session, doc_id=document_id)
    page_count = doc_ver.page_count
    if page_count != len(target_page_uuids):
        err_msg = (
            "Invalid number of target page uuids: "
            f"page_count={page_count} != {len(target_page_uuids)}"
        )
        raise ValueError(err_msg)

    with db_session as session:
        new_doc_ver = DocumentVersion(
            id=target_docver_uuid,
            document_id=document_id,
            number=doc_ver.number + 1,
            file_name=doc_ver.file_name,
            page_count=doc_ver.page_count,
            short_description="With OCR text layer",
        )
        session.add(new_doc_ver)

        for page_number in range(1, new_doc_ver.page_count + 1):
            page = Page(
                id=target_page_uuids[page_number - 1],
                document_version_id=target_docver_uuid,
                number=page_number,
                lang=lang,
            )
            session.add(page)

        session.commit()


def update_doc_ver_text(
    db_session: Session, doc_ver_id: UUID, streams: list[io.StringIO]
):
    pages = get_pages(db_session, doc_ver_id=doc_ver_id)
    with db_session as session:
        for page, stream in zip(pages, streams):
            db_page = session.get(Page, page.id)
            db_page.text = stream.read()
        session.commit()
