from __future__ import annotations

from pathlib import Path
from rai_sdk_harness.sequence_logger import SequenceLogger
from time import sleep

sequence_logger = SequenceLogger(Path(".").absolute())

# Print "original" `log_file_path`
print(f"log_file_path: {sequence_logger.log_file_path}")

# Log to "original" log file
sequence_logger.warn("WARNING - 1")
sequence_logger.info("MESSAGE - 1")
sequence_logger.info("MESSAGE - 2")
sequence_logger.err("ERROR - 1")
sequence_logger.err("ERROR - 2")
sequence_logger.warn("WARNING - 2")
sequence_logger.info("MESSAGE - 3")

# Wait a sec...
print("")
print("'Refreshing' log path (and making you wait)...")
sleep(1)

# Generate new `log_file_path`
sequence_logger.refresh_log_file_path()
print(f"log_file_path: {sequence_logger.log_file_path}")

# Log to new log
sequence_logger.err("ERROR - 1")
sequence_logger.info("MESSAGE - 2")
sequence_logger.warn("WARNING - 1")
sequence_logger.err("ERROR - 2")
sequence_logger.err("ERROR - 3")
sequence_logger.info("MESSAGE - 2")
sequence_logger.warn("WARNING - 2")
