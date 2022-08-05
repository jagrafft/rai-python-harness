from __future__ import annotations

from time import localtime, strftime

import logging


def formatted_time_now() -> str:
    return strftime("%Y-%m-%dT%H%M%S", localtime())


def init_logger(log_path: Path) -> logging.Logger:
    """Initiate a `logging.Logger` object at `log_path`"""
    logging.basicConfig(datefmt="%Y-%m-%dT%H%M%S.%.3f")

    log_file_handler = logging.FileHandler(str(log_path))
    log_file_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(str(log_path))
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_file_handler)

    return logger
