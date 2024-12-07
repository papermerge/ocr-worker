import io
from uuid import UUID

from sqlalchemy import exc, select
from sqlalchemy.orm import Session

from ocrworker import schema
from ocrworker.db.orm import Document, DocumentVersion, Page


def get_doc(db_session: Session, doc_id: UUID) -> schema.Document:
    stmt = select(Document).where(Document.id == doc_id)
    db_doc = db_session.scalars(stmt).one()
    model_doc = schema.Document.model_validate(db_doc)

    return model_doc


def get_docs(db_session: Session, doc_ids: list[UUID]) -> list[schema.Document]:

    stmt = select(Document).where(Document.id.in_(doc_ids))
    db_docs = db_session.scalars(stmt).all()
    model_docs = [schema.Document.model_validate(db_doc) for db_doc in db_docs]

    return model_docs


def get_last_version(
    db_session: Session, doc_id: UUID
) -> schema.DocumentVersion:
    """
    Returns last version of the document
    identified by doc_id
    """
    stmt = (
        select(DocumentVersion)
        .join(Document)
        .where(
            DocumentVersion.document_id == doc_id,
        )
        .order_by(DocumentVersion.number.desc())
        .limit(1)
    )
    db_doc_ver = db_session.scalars(stmt).one()
    model_doc_ver = schema.DocumentVersion.model_validate(db_doc_ver)

    return model_doc_ver


def get_doc_ver(
    db_session: Session, id: UUID  # noqa
) -> schema.DocumentVersion:
    """
    Returns last version of the document
    identified by doc_id
    """
    stmt = select(DocumentVersion).where(DocumentVersion.id == id)
    db_doc_ver = db_session.scalars(stmt).one()
    model_doc_ver = schema.DocumentVersion.model_validate(db_doc_ver)

    return model_doc_ver


def get_pages(db_session: Session, doc_ver_id: UUID) -> list[schema.Page]:
    """
    Returns first page of the document version
    identified by doc_ver_id
    """
    result = []

    stmt = (
        select(Page)
        .where(
            Page.document_version_id == doc_ver_id,
        )
        .order_by(Page.number.asc())
    )
    try:
        db_pages = db_session.scalars(stmt).all()
    except exc.NoResultFound:
        raise Exception(
            f"DocVerID={doc_ver_id} does not have pages(s)."
            " Maybe it does not have associated file yet?"
        )
    result = [schema.Page.model_validate(db_page) for db_page in db_pages]

    return list(result)


def get_page(
    db_session: Session,
    id: UUID,
) -> schema.Page:

    stmt = (
        select(Page)
        .join(DocumentVersion)
        .join(Document)
        .where(
            Page.id == id,
        )
    )
    try:
        db_page = db_session.scalars(stmt).one()
    except exc.NoResultFound:
        raise Exception(f"PageID={id} not found")
    result = schema.Page.model_validate(db_page)

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

    new_doc_ver = DocumentVersion(
        id=target_docver_uuid,
        document_id=document_id,
        number=doc_ver.number + 1,
        lang=lang,
        file_name=doc_ver.file_name,
        page_count=doc_ver.page_count,
        short_description="With OCR text layer",
    )
    db_session.add(new_doc_ver)

    for page_number in range(1, new_doc_ver.page_count + 1):
        page = Page(
            id=target_page_uuids[page_number - 1],
            document_version_id=target_docver_uuid,
            number=page_number,
            lang=lang,
            page_count=new_doc_ver.page_count,
        )
        db_session.add(page)

        db_session.commit()


def update_doc_ver_text(
    db_session: Session, doc_ver_id: UUID, streams: list[io.StringIO]
):
    pages = get_pages(db_session, doc_ver_id=doc_ver_id)

    for page, stream in zip(pages, streams):
        db_page = db_session.get(Page, page.id)
        db_page.text = stream.read()

    db_session.commit()
