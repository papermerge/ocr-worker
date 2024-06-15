import io
from logging.config import dictConfig
from pathlib import Path

import yaml
from pikepdf import Pdf


def setup_logging(config: Path):
    if config is None:
        return

    with open(config, "r") as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)

    dictConfig(config)


def get_pdf_page_count(content: io.BytesIO | bytes) -> int:
    if isinstance(content, bytes):
        pdf = Pdf.open(io.BytesIO(content))
    else:
        pdf = Pdf.open(content)
    page_count = len(pdf.pages)
    pdf.close()

    return page_count


def stitch_pdf(srcs: list[Path], dst: Path):
    """
    Creates target pdf file by 'stitching' source (one page)
    pdf files.

    Note that source files are assumed to have only one page.
    * stitch = combine, sew, put together
    """
    target = Pdf.new()
    for src in srcs:
        with Pdf.open(src) as f:
            # source pdf files are assumed to have only one page
            target.pages.append(f.pages[0])

    target.save(dst)
    target.close()
