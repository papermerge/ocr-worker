# OCR Worker

Performs OCR on the documents. Optionally can download/upload documents
from S3 storage.

## Run it:

    poetry run task worker

## Configuration

OCR Worker is configured via environment variables

### PAPERMERGE__DATABASE__URL

Database URL (URI). For details see: [Database URLs](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls)
Default value is `sqlite:////db/db.sqlite3`

Example:

    export PAPERMERGE__DATABASE__URL=sqlite:////opt/cocodb.sqlite3

### PAPERMERGE__REDIS__URL

Redis URL (URI).
If no value is provided, then it will not connect to Redis.

Example:

    export PAPERMERGE__REDIS__URL=redis://localhost:6379/0

### PAPERMERGE__MAIN__LOGGING_CFG

Example:

    export PAPERMERGE__MAIN__LOGGING_CFG=/etc/papermerge/logging.yaml

### PAPERMERGE__MAIN__MEDIA_ROOT

Path to media root. If no value provided, current working directory
is used as media root.

Example:

    export PAPERMERGE__MAIN__MEDIA_ROOT=/opt/media_root
