import logging
import mimetypes
from pathlib import Path
from typing import List
from uuid import UUID

import ocrmypdf

from ocrworker import config, constants, models, plib

logger = logging.getLogger(__name__)
settings = config.get_settings()

STARTED = "started"
COMPLETE = "complete"


def notify_hocr_ready(page_path, **kwargs):
    pass


def notify_txt_ready(page_path, **kwargs):
    pass


def notify_pre_page_ocr(page_path, **kwargs):
    pass


def ocr_document(
    doc_ver: models.DocumentVersion,
    target_docver_uuid: UUID,
    target_page_uuids: List[UUID],
    lang: str,
):
    lang = lang.lower()

    doc_ver_path = plib.abs_docver_path(doc_ver.id, doc_ver.file_name)
    _type, encoding = mimetypes.guess_type(doc_ver_path)
    if _type is None:
        raise ValueError("Mimetype of the")

    if encoding in ("application/pdf", "application/image"):
        _ocr_document(
            doc_ver=doc_ver,
            target_docver_uuid=target_docver_uuid,
            target_page_uuids=target_page_uuids,
            lang=lang,
            preview_width=300,
        )
    elif encoding == "application/tiff":
        """
        # TODO:
        #new_filename = convert_tiff2pdf(
        #    doc_url=abs_path(document_version.file_path)
        #)
        # now .pdf
        #orig_file_name = doc_path.file_name
        #doc_path.file_name = new_filename
        # and continue as usual
        #_ocr_document(
        #    document_version=document_version,
        #    lang=lang,
        #)
        """
    else:
        raise ValueError(f"Unsupported format for document: {doc_ver_path}")

    return True


def _ocr_document(
    doc_ver: models.DocumentVersion,
    target_docver_uuid: UUID,
    target_page_uuids: List[UUID],
    lang: str,
    preview_width: int,
):
    sidecar_dir = Path(settings.MEDIA_ROOT, constants.OCR, constants.PAGES)

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
        uuids=",".join(str(item) for item in target_page_uuids),
        sidecar_format="svg",
        preview_width=preview_width,
        deskew=True,
    )
