from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rai_sdk_harness.schema import Schema
from rai_sdk_harness.sequence_logger import SequenceLogger

# from rai_sdk_harness.utils import formatted_time_now


class Sequence:
    schema: Schema
    sequence_logger: SequenceLogger

    def log_dir() -> Path:
        """Accessor function for `SequenceLogger.log_output_dir`"""
        return sequence_logger.log_output_dir

    def log_path() -> Path:
        """Accessor function for `SequenceLogger.log_file_path`"""
        return sequence_logger.log_file_path

    def refresh_log_path() -> None:
        """Accessor function for `SequenceLogger.refresh_log_file_path()`"""
        sequence_logger.refresh_log_file_path()

    # def run():

    def show(name: str) -> Any:
        """Accessor function for `Schema.get`"""
        return schema.get(name)
