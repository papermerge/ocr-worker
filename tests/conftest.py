import io
import uuid

import pytest

from ocrworker import db
from ocrworker.db import Base, get_engine
from ocrworker.db.models import Document, DocumentVersion, Page, User


@pytest.fixture(scope="function")
def session():
    url = "sqlite:///test_db.sqlite3"
    engine = get_engine(url)
    Base.metadata.create_all(engine)
    db_session = db.get_db(url=url)
    try:
        with db_session() as se:
            yield se
    finally:
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def socrates(session):
    user = User(
        username="socrates", password="truth", email="socrates@gmail.com"
    )
    session.add(user)
    session.commit()

    return user


@pytest.fixture(scope="function")
def doc_factory(session, socrates):

    def _create_doc(
        title: str, file_name: str = "receipt_001.pdf", page_count: int = 2
    ):
        doc_id = uuid.uuid4()
        doc_ver_id = uuid.uuid4()
        doc = Document(
            id=doc_id,
            ctype="document",
            title=title,
            lang="en",
            user_id=socrates.id,
        )
        doc_ver = DocumentVersion(
            id=doc_ver_id,
            number=1,
            file_name=file_name,
            document_id=doc_id,
            page_count=page_count,
        )

        session.add_all([doc, doc_ver])
        for page_number in range(1, page_count + 1):
            page = Page(
                id=uuid.uuid4(),
                number=page_number,
                document_version_id=doc_ver_id,
            )
            session.add(page)

        session.commit()

        return doc

    return _create_doc


@pytest.fixture(scope="function")
def page_factory(session, socrates):

    def _create_page(title: str, text: str = "", page_number: int = 1):
        doc_id = uuid.uuid4()
        doc_ver_id = uuid.uuid4()
        doc = Document(
            id=doc_id,
            ctype="document",
            title=title,
            lang="en",
            user_id=socrates.id,
        )
        doc_ver = DocumentVersion(
            id=doc_ver_id, number=1, file_name=title, document_id=doc_id
        )

        session.add_all([doc, doc_ver])

        page = Page(
            id=uuid.uuid4(),
            number=page_number,
            text=text,
            document_version_id=doc_ver_id,
        )
        session.add(page)

        session.commit()

        return page

    return _create_page


@pytest.fixture(scope="function")
def doc_ver_factory(session, socrates):

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
            lang="en",
            user_id=socrates.id,
        )
        doc_ver = DocumentVersion(
            id=doc_ver_id,
            number=1,
            file_name=file_name,
            document_id=doc_id,
            page_count=page_count,
        )

        session.add_all([doc, doc_ver])
        if streams:
            if len(streams) != page_count:
                raise ValueError("Streams count should be same as page count")

            for page_number, stream in zip(range(1, page_count + 1), streams):
                page = Page(
                    id=uuid.uuid4(),
                    number=page_number,
                    document_version_id=doc_ver_id,
                    text=stream.read(),
                )
                session.add(page)
        else:
            for page_number in range(1, page_count + 1):
                page = Page(
                    id=uuid.uuid4(),
                    number=page_number,
                    document_version_id=doc_ver_id,
                )
                session.add(page)

        session.commit()

        return doc_ver

    return _create_doc_ver
