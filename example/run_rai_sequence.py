from __future__ import annotations

# Load dependencies for `run_rai_sequence.py` functionality (OPTIONAL)
from os import environ, makedirs

# Ensure environment variables are set (OPTIONAL)
for var in ["RAI_PROFILE", "RAI_DB", "RAI_ENGINE"]:
    if var not in environ:
        exit(f"Must set environment variable '{var}'")

# Load dependencies for `run_rai_sequence.py` functionality
from datetime import datetime  # (OPTIONAL)
from pathlib import Path  # `rai_python_harness` classes require `Path`s

# RAI Python SDK
from railib import api, config

# Import classes from RAI Python Harness
from rai_python_harness.sequence import Sequence
from rai_python_harness.sequence_logger import SequenceLogger
from rai_python_harness.schema import Schema

# Create RAI Context
context = api.Context(**config.read(profile=environ["RAI_PROFILE"]))

# Generate log path
# NB. Optional to do so here, _must_ be provided to `SequenceLogger` class
log_path = Path(
    f"logs/load_data/{datetime.now().strftime('%Y-%m-%dT%H%M%S')}"
).absolute()

# Ensure log path does not overwrite (OPTIONAL)
try:
    makedirs(log_path)
except:
    exit(f"EXECUTION STOPPED: log path '{log_path}' exists, please address")

# Load TOML file with run sequence
# NB. TOML is validated by the `Schema` class prior instantiation,
#     and will fail (with informative report) _prior to_ creation
#     on error
schema = Schema(Path("project/run_sequence.toml"))

# Initialize logger
sequence_logger = SequenceLogger(log_path)

# Initialize `Sequence` class
sequence = Sequence(context, schema, sequence_logger)

# Set `database` and `engine` of `sequence`
sequence.database = environ["RAI_DB"]
sequence.engine = environ["RAI_ENGINE"]

# Check if database exists
# DELETE if so
print(f"Creating database '{environ['RAI_DB']}'...")
if api.get_database(context, environ["RAI_DB"]):
    api.delete_database(context, environ["RAI_DB"])

# Create database
api.create_database(context, environ["RAI_DB"])

# Execute RAI Run Sequence
print("Executing sequence...")
sequence.exec()
