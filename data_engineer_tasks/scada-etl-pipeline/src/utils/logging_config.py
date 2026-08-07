"""
Structured (JSON) logging so pipeline logs are directly queryable in
log aggregators (CloudWatch, ELK, Loki, etc.) instead of being free-text.
"""

import logging
import sys

from pythonjsonlogger import jsonlogger

from src.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(settings.log_level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
