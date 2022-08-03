from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rai_sdk_harness.utils import formatted_time_now


@dataclass
class SequenceLogger:
    log_output_dir: Path

    def __post_init__(self):
        if not log_output_dir.is_dir():
            exit(f"EXECUTION STOPPED: '{log_output_dir}' is not a directory")

    _run_times = {"post_init": formatted_time_now()}

    import logging
