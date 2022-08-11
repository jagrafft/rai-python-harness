from __future__ import annotations

from pathlib import Path
from rai_python_harness.schema import Schema

keys_to_show = [
    "data_dir",
    "source_dir",
    "queries",
    "non_extant_key_001",
    "non_extant_key_2389",
]

schema = Schema(Path("tests/project/test_queries.toml"))

for key in keys_to_show:
    try:
        print(f"{key}: {schema.get(key)}")
        print(f"type(val): {type(schema.get(key))}")
    except KeyError as key_err:
        print(f"ERROR: {key_err}")

    print("")
