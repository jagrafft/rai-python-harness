from __future__ import annotations

from pathlib import Path
from time import localtime, strftime

import logging
import re


def cell_has_inputs(cell: dict) -> bool:
    """Return whether or not 'inputs' key of `cell` is present and populated"""
    return True if ("inputs" in cell) and cell["inputs"] else False


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


def open_file(file_path: Path) -> str:
    """Open file at `file_path` or raise `FileNotFoundError`"""
    try:
        f = open(file_path, "r")
        contents = f.read()
        f.close()
        return contents
    except FileNotFoundError:
        raise FileNotFoundError(f"File Not Found at '{file_path}'")


def sanitize_query_name(qry: dict) -> str:
    """Return a 'sanitized' name for a query"""
    reg_x = re.compile("[_\w]+")
    return "_".join(re.findall(reg_x, qry["name"]))


def write_file(file_path: Path, contents: str) -> None:
    of = open(file_path, "wb")
    of.write(bytes(contents, "utf-8"))
    of.close()
