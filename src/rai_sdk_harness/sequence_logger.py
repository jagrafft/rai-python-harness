from __future__ import annotations

from dataclasses import dataclass  # , field
from pathlib import Path

from rai_sdk_harness.utils import formatted_time_now


@dataclass
class SequenceLogger:
    log_output_dir: Path

    def __post_init__(self):
        if not log_output_dir.is_dir():
            exit(f"EXECUTION STOPPED: '{log_output_dir}' is not a directory")

    import logging

    _run_times = {"logger init": formatted_time_now()}
