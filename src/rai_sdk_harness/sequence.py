from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rai_sdk_harness.schema import Schema
from rai_sdk_harness.sequence_logger import SequenceLogger

# from rai_sdk_harness.utils import formatted_time_now


@dataclass
class Sequence:
    schema: Schema
    sequence_logger: SequenceLogger

    # def exec(self, do_not_connect: bool = False):
    # """Execute each cell in `schema.query` using `schema.get("compute")` in the database `schema.get("database")`. _Or_ perform all save execution if `do_not_connect=True`."""

    def log_dir(self) -> Path:
        """Accessor function for `SequenceLogger.log_output_dir`"""
        return self.sequence_logger.log_output_dir

    def log_path(self) -> Path:
        """Accessor function for `SequenceLogger.log_file_path`"""
        return self.sequence_logger.log_file_path

    def refresh_log_path(self) -> None:
        """Accessor function for `SequenceLogger.refresh_log_file_path()`"""
        self.sequence_logger.refresh_log_file_path()

    def show(self, name: str) -> Any:
        """Accessor function for `Schema.get`"""
        return self.schema.get(name)
