import uuid
from typing import Optional

import typer
from typing_extensions import Annotated

from ocrworker import db, config


app = typer.Typer(help="OCR documents")
settings = config.get_settings()
Session = db.get_db()

DocIDsType = Annotated[
    Optional[list[uuid.UUID]],
    typer.Argument()
]


@app.command(name="ocr")
def ocr_cmd(
    doc_ids: DocIDsType = None,
    dry_run: bool = False,
):

    with Session() as db_session:
        docs = db.get_docs(db_session, doc_ids)
        items = []  # to be added to the index
        for doc in docs:
            pass

