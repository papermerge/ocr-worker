import yaml
from pathlib import Path
from logging.config import dictConfig


def setup_logging(config: Path):
    if config is None:
        return

    with open(config, 'r') as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)

    dictConfig(config)
