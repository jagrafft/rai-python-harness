from __future__ import annotations

from pathlib import Path
from rai_sdk_harness.schema import Schema

s = Schema(Path("../test_schema.toml"))

for v in ["w00t", "compute", "version_control", "sjadkfl"]:
    print(f"testing key: {v}")
    try:
        print(f"val: {s.get(v)}")
        print(f"type(val): {type(s.get(v))}")
    except KeyError as kerr:
        print(f"ERROR: {kerr}")

    print("")
