from  pathlib import Path
from logging import config
from .transfer import Transfer
import yaml
with open(file=Path(__file__).parent.parent.parent/"conf/logging.yaml", mode='r', encoding="utf-8") as file:
    logging_yaml = yaml.load(stream=file, Loader=yaml.FullLoader)
    config.dictConfig(logging_yaml)