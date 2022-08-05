from __future__ import annotations

from pathlib import Path
from railib import api, config

from rai_sdk_harness.sequence import Sequence
from rai_sdk_harness.sequence_logger import SequenceLogger
from rai_sdk_harness.schema import Schema
from time import sleep

keys_to_show = [
    "description",
    "authors",
    "database",
    "compute",
    "version_control",
    "non_extant_key_001",
    "non_extant_key_2389",
]

context = api.Context(**config.read())

schema = Schema(Path("tests/run_script/test_schema.toml"))
sequence_logger = SequenceLogger(Path.cwd())
seq = Sequence(context, schema, sequence_logger)

sequence_logger.info(f"log_dir: {seq.log_dir()}")
sequence_logger.info(f"log_path: {seq.log_path()}")

sequence_logger.info(f"compute: {seq.compute}")
sequence_logger.info(f"database: {seq.database}")
sequence_logger.info(f"data_dir: {seq.data_dir}")
sequence_logger.info(f"source_dir: {seq.source_dir}")

sequence_logger.info("Waiting then updating parameters...")
sleep(1)
sequence_logger.info("Updating log path...")
seq.refresh_log_path()

sequence_logger.info("Updating compute...")
seq.compute = "UPDATED_COMPUTE"

sequence_logger.info("Updating database...")
seq.database = "UPDATED_DATABASE"

sequence_logger.info("Updating data_dir...")
seq.data_dir = Path(Path.home() / "UPATED_DATA_DIR")

sequence_logger.info("Updating source_dir...")
seq.source_dir = Path(Path.home() / "UPDATED_SOURCE_DIR")

sequence_logger.info(f"log_path: {seq.log_path()}")
sequence_logger.info(f"compute: {seq.compute}")
sequence_logger.info(f"database: {seq.database}")
sequence_logger.info(f"data_dir: {seq.data_dir}")
sequence_logger.info(f"source_dir: {seq.source_dir}")

sequence_logger.info("`show`ing select keys")

sequence_logger.info(f"keys: {keys_to_show}")

for key in keys_to_show:
    try:
        sequence_logger.info(f"{key}: {schema.get(key)}")
        sequence_logger.info(f"type(val): {type(schema.get(key))}")
    except KeyError as key_err:
        sequence_logger.err(f"ERROR: {key_err}")

sequence_logger.info("COMPLETE")
