import uuid
from pathlib import Path

import typer

from ocrworker.ocr import run_one_page_ocr
from ocrworker.utils import stitch_pdf

app = typer.Typer(help="OCR documents")


@app.command(name="ocrmypdf")
def ocrmypdf_cmd(
    file_path: Path,
    output_dir: Path,
    sidecar_dir: Path,
    page_number: int = 1,
    lang: str = "deu",
    preview_width: int = 300,
):
    """Raw OCR command - invokes directly ocrmypdf module"""
    target_page_id = uuid.uuid4()
    print(f"Target page ID={target_page_id}")

    run_one_page_ocr(
        file_path=file_path,
        output_dir=output_dir,
        sidecar_dir=sidecar_dir,
        uuid=target_page_id,
        page_number=page_number,
        lang=lang,
        preview_width=preview_width,
    )


@app.command(name="ocr")
def ocr_cmd(): ...


@app.command(name="stitch")
def stitch_cmd(dst: Path, srcs: list[Path]):
    stitch_pdf(srcs=srcs, dst=dst)
