from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, field

from rai_sdk_harness.validation import valid_schema_or_exit


@dataclass
class Schema:
    toml_path: Path
    schema: dict = field(init=False)

    def __post_init__(self):
        self.schema = valid_schema_or_exit(self.toml_path)
        # Ensure entries in 'queries' are valid (NOT YET IMPLEMENTED)
        # valid_queries_or_exit(self.schema)

    def get(self, name):
        """Return value associated with 'name' from the dictionary `self.schema`."""
        if name in self.schema:
            return self.schema[f"{name}"]
        else:
            raise ValueError(f"Key '{name}' does not exist")
