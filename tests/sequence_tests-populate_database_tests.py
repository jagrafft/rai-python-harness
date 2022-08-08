from __future__ import annotations

from os import environ

try:
    environ["RAI_DB"]
except:
    exit("Must set environment variable 'RAI_DB'")

try:
    environ["RAI_ENGINE"]
except:
    exit("Must set environment variable 'RAI_ENGINE'")

from pathlib import Path
from railib import api, config

from rai_sdk_harness.sequence import Sequence
from rai_sdk_harness.sequence_logger import SequenceLogger
from rai_sdk_harness.schema import Schema

# Example of executing multiple "phases", each defined by it's
# own TOML file, using the same `SequenceLogger`

# Parameters used for all `Sequence`s
context = api.Context(**config.read())
database = environ["RAI_DB"]
engine = environ["RAI_ENGINE"]
sequence_logger = SequenceLogger(Path.cwd())

# Load `Schema` for each phase from TOML file
schemas = {
    "data": Schema(Path("tests/project/data_load.toml")),
    "models": Schema(Path("tests/project/install_models.toml")),
    "queries": Schema(Path("tests/project/test_queries.toml")),
}

# Create `Sequence` for each phase
sequences = {
    phase: Sequence(context, schema, sequence_logger)
    for phase, schema in schemas.items()
}

# Set consistent database and engine across all `Sequence`s
for seq in sequences.values():
    seq.database = database
    seq.engine = engine

print(f"Creating database '{database}'...")
# Ensure database is empty
if api.get_database(context, database):
    api.delete_database(context, database)

api.create_database(context, database)

# Execute each phase's `Sequence`
for phase, seq in sequences.items():
    print(f"Running phase '{phase}'...")
    res = seq.exec()
    print(res)
