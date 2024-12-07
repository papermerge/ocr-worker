import io
import uuid

from ocrworker import db


def test_increment_doc_version(db_session, doc_factory):
    doc = doc_factory(title="receipt_001.pdf", page_count=2)
    target_docver_uuid = uuid.uuid4()
    target_page_uuids = [uuid.uuid4(), uuid.uuid4()]

    last_ver = db.get_last_version(db_session, doc.id)

    db.increment_doc_ver(
        db_session,
        document_id=doc.id,
        target_docver_uuid=target_docver_uuid,
        target_page_uuids=target_page_uuids,
        lang=doc.lang,
    )

    new_last_ver = db.get_last_version(db_session, doc.id)
    new_pages = db.get_pages(db_session, new_last_ver.id)
    new_ids = {page.id for page in new_pages}

    assert new_last_ver.number == last_ver.number + 1
    assert new_last_ver.id == target_docver_uuid
    assert len(new_pages) == 2
    assert new_ids == set(target_page_uuids)


def test_update_doc_ver_text(db_session, doc_ver_factory):
    doc_ver = doc_ver_factory(
        title="receipt_001.pdf",
        page_count=2,
        streams=[io.StringIO("Text of page 1"), io.StringIO("Text of page 2")],
    )

    db.update_doc_ver_text(
        db_session,
        doc_ver.id,
        streams=[
            io.StringIO("Updated text of page 1"),
            io.StringIO("Updated text of page 2"),
        ],
    )

    pages = db.get_pages(db_session, doc_ver.id)
    actual_txt = {page.text for page in pages}
    expected_txt = {"Updated text of page 1", "Updated text of page 2"}

    assert actual_txt == expected_txt
