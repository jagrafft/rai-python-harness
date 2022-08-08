from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rai_python_harness.validation import valid_schema_or_exit


@dataclass
class Schema:
    """Loads, validates, then serves as a 'wrapper' for the TOML file
    specifying the run sequence.

    NOTE: Requires 'proper' input, and will fail on then report a violation
    """

    toml_path: Path
    schema: dict = field(init=False)

    def __post_init__(self) -> None:
        self.schema = valid_schema_or_exit(self.toml_path)
        # Ensure entries in 'queries' are valid (NOT YET IMPLEMENTED)
        # valid_queries_or_exit(self.schema)

    def get(self, name) -> Any:
        """Return value associated with 'name' from the dictionary `self.schema`."""
        if name in self.schema:
            return self.schema[f"{name}"]
        else:
            raise KeyError(f"'{name}' does not exist")
