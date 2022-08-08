from __future__ import annotations

from pathlib import Path
from rai_python_harness.sequence_logger import SequenceLogger
from time import sleep

sequence_logger = SequenceLogger(Path.cwd().absolute())

sequence_logger.info(f"log_output_dir: {sequence_logger.log_output_dir}")
sequence_logger.info(f"log_file_path: {sequence_logger.log_file_path}")
sequence_logger.err("ERROR - 1")
sequence_logger.info("MESSAGE - 1")
sequence_logger.warn("WARNING - 1")
sequence_logger.err("ERROR - 2")
sequence_logger.info("MESSAGE - 2")
sequence_logger.warn("WARNING - 2")
sequence_logger.info("MESSAGE - 3")

sequence_logger.info("'Refreshing' log path (and making you wait)...")
sleep(1)

sequence_logger.refresh_log_file_path()

sequence_logger.info(f"log_output_dir: {sequence_logger.log_output_dir}")
sequence_logger.info(f"log_file_path: {sequence_logger.log_file_path}")
sequence_logger.warn("WARNING - 1")
sequence_logger.err("ERROR - 1")
sequence_logger.warn("WARNING - 2")
sequence_logger.info("MESSAGE - 2")
sequence_logger.err("ERROR - 2")
sequence_logger.err("ERROR - 3")

sequence_logger.info("'Refreshing' log directory (and making you wait)...")
sleep(1)

sequence_logger.log_output_dir = Path.home()
sequence_logger.refresh_log_file_path()

sequence_logger.info(f"log_output_dir: {sequence_logger.log_output_dir}")
sequence_logger.info(f"log_file_path: {sequence_logger.log_file_path}")
sequence_logger.err("ERROR - 1")
sequence_logger.err("ERROR - 2")
sequence_logger.err("ERROR - 3")
sequence_logger.info("MESSAGE - 1")
sequence_logger.info("MESSAGE - 2")
sequence_logger.warn("WARNING - 1")
sequence_logger.warn("WARNING - 2")

sequence_logger.info("'Refreshing' log path (and making you wait)...")
sleep(1)

sequence_logger.refresh_log_file_path()

sequence_logger.info(f"log_output_dir: {sequence_logger.log_output_dir}")
sequence_logger.info(f"log_file_path: {sequence_logger.log_file_path}")
sequence_logger.info("MESSAGE - 1")
sequence_logger.warn("WARNING - 1")
sequence_logger.err("ERROR - 1")
sequence_logger.err("ERROR - 2")
sequence_logger.err("ERROR - 3")
sequence_logger.info("MESSAGE - 2")
sequence_logger.warn("WARNING - 2")
