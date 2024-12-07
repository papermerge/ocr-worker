import io
import uuid

import pytest

from ocrworker.db.engine import engine, Session
from ocrworker.db import Base
from ocrworker.db.orm import Document, DocumentVersion, Page, User


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(engine, checkfirst=False)
    with Session() as session:
        yield session

    Base.metadata.drop_all(engine, checkfirst=False)


@pytest.fixture(scope="function")
def socrates(db_session):
    user = User(
        username="socrates", password="truth", email="socrates@gmail.com"
    )
    db_session.add(user)
    db_session.commit()

    return user


@pytest.fixture(scope="function")
def doc_factory(db_session, socrates):

    def _create_doc(
        title: str, file_name: str = "receipt_001.pdf", page_count: int = 2
    ):
        doc_id = uuid.uuid4()
        doc_ver_id = uuid.uuid4()
        doc = Document(
            id=doc_id,
            ctype="document",
            title=title,
            lang="deu",
            user_id=socrates.id,
        )
        doc_ver = DocumentVersion(
            id=doc_ver_id,
            number=1,
            file_name=file_name,
            lang="deu",
            document_id=doc_id,
            page_count=page_count,
        )

        db_session.add_all([doc, doc_ver])
        for page_number in range(1, page_count + 1):
            page = Page(
                id=uuid.uuid4(),
                number=page_number,
                page_count=page_count,
                document_version_id=doc_ver_id,
            )
            db_session.add(page)

        db_session.commit()

        return doc

    return _create_doc


@pytest.fixture(scope="function")
def page_factory(db_session, socrates):

    def _create_page(
        title: str, text: str = "", page_number: int = 1, page_count: int = 3
    ):
        doc_id = uuid.uuid4()
        doc_ver_id = uuid.uuid4()
        doc = Document(
            id=doc_id,
            ctype="document",
            title=title,
            lang="deu",
            user_id=socrates.id,
        )
        doc_ver = DocumentVersion(
            id=doc_ver_id,
            number=1,
            file_name=title,
            document_id=doc_id,
            lang="deu",
        )

        db_session.add_all([doc, doc_ver])

        page = Page(
            id=uuid.uuid4(),
            number=page_number,
            text=text,
            document_version_id=doc_ver_id,
            page_count=page_count,
        )
        db_session.add(page)

        db_session.commit()

        return page

    return _create_page


@pytest.fixture(scope="function")
def doc_ver_factory(db_session, socrates):

    def _create_doc_ver(
        title: str,
        file_name: str = "receipt_001.pdf",
        page_count: int = 2,
        streams: list[io.StringIO] | None = None,
    ):
        doc_id = uuid.uuid4()
        doc_ver_id = uuid.uuid4()
        doc = Document(
            id=doc_id,
            ctype="document",
            title=title,
            lang="deu",
            user_id=socrates.id,
        )
        doc_ver = DocumentVersion(
            id=doc_ver_id,
            number=1,
            file_name=file_name,
            document_id=doc_id,
            lang="deu",
            page_count=page_count,
        )

        db_session.add_all([doc, doc_ver])
        if streams:
            if len(streams) != page_count:
                raise ValueError("Streams count should be same as page count")

            for page_number, stream in zip(range(1, page_count + 1), streams):
                page = Page(
                    id=uuid.uuid4(),
                    number=page_number,
                    document_version_id=doc_ver_id,
                    page_count=page_count,
                    text=stream.read(),
                )
                db_session.add(page)
        else:
            for page_number in range(1, page_count + 1):
                page = Page(
                    id=uuid.uuid4(),
                    number=page_number,
                    page_count=page_count,
                    document_version_id=doc_ver_id,
                )
                db_session.add(page)

        db_session.commit()

        return doc_ver

    return _create_doc_ver
