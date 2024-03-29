from __future__ import annotations

from dataclasses import dataclass, field
from logging import Logger
from pathlib import Path
from typing import ClassVar

from rai_python_harness.utils import formatted_time_now, init_logger


@dataclass
class SequenceLogger:
    _log_output_dir: Path
    log_file_path: Path = field(init=False)
    logger: Logger = field(init=False)

    def __post_init__(self) -> None:
        if not self._log_output_dir.is_dir():
            exit(f"EXECUTION STOPPED: '{self.log_output_dir}' is not a directory")

        self.log_output_dir = self._log_output_dir
        self.log_file_path = Path(self.log_output_dir / f"{formatted_time_now()}.log")
        self.logger = init_logger(self.log_file_path)

    @property
    def log_output_dir(self) -> Path:
        return self._log_output_dir

    @log_output_dir.setter
    def log_output_dir(self, path: Path) -> None:
        self._log_output_dir = path

    def err(self, msg: str, exc_info: bool = True) -> None:
        """Log error message"""
        self.logger.error(msg, exc_info=exc_info)

    def info(self, msg: str, exc_info: bool = False) -> None:
        """Log information message"""
        self.logger.info(msg, exc_info=exc_info)

    def refresh_log_file_path(self) -> None:
        """Creates new `logging.Logger` with `log_file_path` set to (approximate) current time"""
        self.log_file_path = Path(self.log_output_dir / f"{formatted_time_now()}.log")
        self.logger = init_logger(self.log_file_path)

    def warn(self, msg: str, exc_info: bool = False) -> None:
        """Log warning message"""
        self.logger.warning(msg, exc_info=exc_info)
