import uuid

import typer

from ocrworker import config, db
from ocrworker.tasks import ocr_document_task

app = typer.Typer(help="OCR documents")
settings = config.get_settings()
Session = db.get_db()


@app.command(name="ocr")
def ocr_cmd(doc_id: uuid.UUID, lang: str):

    ocr_document_task(document_id=doc_id, lang=lang)
