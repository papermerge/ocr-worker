FROM python:3.13-alpine

WORKDIR /app
ENV VIRTUAL_ENV=/app/venv

RUN apk update && apk add linux-headers \
    python3-dev \
    gcc \
    libc-dev \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-data-deu \
    tesseract-ocr-data-spa \
    tesseract-ocr-data-ron \
    libpq-dev \
    imagemagick \
    ghostscript \
    poppler-utils

COPY poetry.lock pyproject.toml README.md LICENSE /app/

RUN pip install --upgrade poetry && \
    poetry install -E pg -v

COPY ocrworker /app/ocrworker/
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["worker"]
