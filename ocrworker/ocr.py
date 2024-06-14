import tempfile
from pathlib import Path
from uuid import UUID

import ocrmypdf
from pikepdf import Pdf


def run_ocr(
    file_path: Path,
    output_dir: Path,
    sidecar_dir: Path,
    uuid: UUID,  # target page UUID
    lang: str,
    page_number: int = 1,
    preview_width: int = 300,
):
    """
    Run OCR on PDF file for one page only.

    OCR page is specified with `page_number` argument.
    `page_number` starts with 1 i.e. first page
    in the document has number 1.
    """
    pdf = Pdf.open(file_path)

    if page_number <= 0:
        raise ValueError("Page number must be at least '1'")

    if page_number > len(pdf.pages):
        raise ValueError(
            f"File {file_path} has {len(pdf.pages)}. "
            f"Request page number '{page_number}' out of range"
        )

    with Pdf.open(file_path) as pdf, tempfile.NamedTemporaryFile() as temp:
        if len(pdf.pages) > 1:
            dst = Pdf.new()
            # extract page number `page_number` into temporary file
            # (one page pdf) and continue working with it
            for n, page in enumerate(pdf.pages):
                if n + 1 == page_number:
                    dst.pages.append(page)
                    break
            dst.save(temp.name)
            dst.close()
            # ocrmypdf will ocr only one page
            file_path = temp.name

        ocrmypdf.ocr(
            file_path,
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
            uuid=str(uuid),
            pages="1",  # OCR only one page
            sidecar_format="svg",
            preview_width=preview_width,
            deskew=True,
        )
