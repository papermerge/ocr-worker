import logging
from celery import Celery
from ocrworker import config, utils
from celery.signals import setup_logging


settings = config.get_settings()
logger = logging.getLogger(__name__)

app = Celery(
    "ocrworker",
    broker=settings.papermerge__redis__url,
    backend=settings.papermerge__redis__url,
    include=["ocrworker.tasks"],
)

app.conf.update(broker_connection_retry_on_startup=True)

app.autodiscover_tasks()


@setup_logging.connect
def config_loggers(*args, **kwags):
    if settings.papermerge__main__logging_cfg:
        utils.setup_logging(settings.papermerge__main__logging_cfg)


def prefixed(name: str) -> str:
    pref = settings.papermerge__main__prefix
    if pref:
        return f"{pref}_{name}"

    return name


app.conf.task_routes = {
    "i3": {"queue": prefixed("i3")},
    "ocr": {"queue": prefixed("ocr")},
}


if __name__ == "__main__":
    app.start()
