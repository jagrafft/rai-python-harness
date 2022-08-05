from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from railib import api
from typing import Any

from rai_sdk_harness.query_utils import data_query, log_result
from rai_sdk_harness.schema import Schema
from rai_sdk_harness.sequence_logger import SequenceLogger

from rai_sdk_harness.utils import cell_has_inputs, open_file, query_name


@dataclass
class Sequence:
    context: api.Context
    schema: Schema
    sequence_logger: SequenceLogger
    # Non-initialized variables are bound "in post" to accommodate CLI args
    _compute: str = field(init=False)
    _database: str = field(init=False)
    _data_dir: Path = field(init=False)
    _source_dir: Path = field(init=False)

    def __post_init__(self):
        # Bind variables to CLI args (highest rank) or contents of TOML file (default)
        self.compute = self.schema.get("compute")
        self.database = self.schema.get("database")
        self.data_dir = Path(Path.cwd() / self.schema.get("data_dir"))
        self.source_dir = Path(Path.cwd() / self.schema.get("source_dir"))

    @property
    def compute(self) -> str:
        return self._compute

    @compute.setter
    def compute(self, name: str) -> None:
        self._compute = name

    @property
    def database(self) -> str:
        return self._database

    @database.setter
    def database(self, name: str) -> None:
        self._database = name

    @property
    def data_dir(self) -> Path:
        return self._data_dir

    @data_dir.setter
    def data_dir(self, path: Path) -> None:
        self._data_dir = path

    @property
    def source_dir(self) -> Path:
        return self._source_dir

    @source_dir.setter
    def source_dir(self, path: Path) -> None:
        self._source_dir = path

    def exec(self) -> None:
        """Execute each cell in `schema.query` using `schema.get("compute")` in the database `schema.get("database")`."""

        # Iterate 'queries' array and dispatch queries entry-by-entry
        for qry in self.schema.get("queries"):
            self.sequence_logger.info(
                f"{qry['index']}: {query_name} ({qry['type'].upper()})"
            )

            # Path for source file
            source_path = Path(self.source_dir / qry["file_path"])

            self.sequence_logger.info(f"Attempting to load '{source_path}'")
            try:
                source = open_file(source_path)
            except FileNotFoundError:
                self.sequence_logger.err(f"'{source_path}' not found, exiting")
                exit()

            inputs = None
            if cell_has_inputs(qry):
                logger.info("Reading inputs from disk...")
                inputs = {
                    key: open_file(Path(self.data_dir / input_file))
                    for entry in qry["inputs"]
                    for key, input_file in entry.items()
                }

            # Generate a (partially) 'sanitized' name for query
            name = query_name(qry)

            # Variable to hold results of query operation
            result = None

            query_type_uppercase = qry["type"].upper()

            # Dispatch based on query type
            if query_type_uppercase in ["QUERY", "UPDATE"]:
                self.sequence_logger(f"Running {qry['type']}...")
                result = api.query(
                    self.context,
                    self.database,
                    self.compute,
                    readonly=(query_type_uppercase == "UPDATE"),
                    inputs=inputs,
                )
            elif query_type_uppercase == "INSTALL":
                self.sequence_logger("Bundling model(s)...")
                model = {}
                model[f"{source_path.name.replace('.rel', '')}"] = source

                self.sequence_logger("Installing model(s)...")
                result = api.install_model(
                    self.context, self.database, self.compute, model
                )
            elif query_type_uppercase == "DATA":
                self.sequence_logger(f"Loading data...")
                result = data_query(
                    self.context, inputs, source, name, self.sequence_logger
                )
            else:
                self.sequence_logger.warn(
                    f"Query type {qry['type']} not recognized, skipping..."
                )

            log_result(result, qry["index"], name, self.sequence_logger)

    def log_dir(self) -> Path:
        """Accessor function for `SequenceLogger.log_output_dir`"""
        return self.sequence_logger.log_output_dir

    def log_path(self) -> Path:
        """Accessor function for `SequenceLogger.log_file_path`"""
        return self.sequence_logger.log_file_path

    def refresh_log_path(self) -> None:
        """Accessor function for `SequenceLogger.refresh_log_file_path()`"""
        self.sequence_logger.refresh_log_file_path()

    def show(self, name: str) -> Any:
        """Accessor function for `Schema.get`"""
        return self.schema.get(name)
