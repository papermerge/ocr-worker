#!/bin/sh

CMD="$1"

if [ -z $CMD ]; then
  echo "No command specified"
  exit 1
fi

exec_worker() {
  cd /app && poetry run celery -A ocrworker.celery_app worker ${OCR_WORKER_ARGS}
}

case $CMD in
  worker)
    exec_worker
    ;;
  *)
    exec "$@"
    ;;
esac
