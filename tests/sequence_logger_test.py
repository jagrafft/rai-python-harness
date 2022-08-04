from __future__ import annotations

from pathlib import Path
from rai_sdk_harness.sequence_logger import SequenceLogger
from time import sleep

sl = SequenceLogger(Path(".").absolute().parent)

# Print "original" `log_file_path`
print(f"log_file_path: {sl.log_file_path}")

# Log to "original" log file
sl.warn("WARNING - 1")
sl.info("MESSAGE - 1")
sl.info("MESSAGE - 2")
sl.err("ERROR - 1")
sl.err("ERROR - 2")
sl.warn("WARNING - 2")
sl.info("MESSAGE - 3")

# Wait a sec...
print("'Refreshing' log path (and making you wait)...")
sleep(1)

# Generate new `log_file_path`
sl.refresh_log_file_path()
print(f"log_file_path: {sl.log_file_path}")

# Log to new log
sl.err("ERROR - 1")
sl.info("MESSAGE - 2")
sl.warn("WARNING - 1")
sl.err("ERROR - 2")
sl.err("ERROR - 3")
sl.info("MESSAGE - 2")
sl.warn("WARNING - 2")
