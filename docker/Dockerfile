FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-spa \
    tesseract-ocr-ron \
    python3-dev \
    libpq-dev \
    imagemagick \
    gcc \
    ghostscript \
    poppler-utils && \
    rm -rf /var/lib/apt/lists/*

COPY poetry.lock pyproject.toml README.md LICENSE /app/
COPY ocrworker/ /app/ocrworker/

RUN pip install --upgrade poetry
RUN poetry install -E pg -v

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["worker"]
