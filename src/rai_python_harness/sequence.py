from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from railib import api
from typing import Any

from rai_python_harness.query_utils import data_query, log_result
from rai_python_harness.schema import Schema
from rai_python_harness.sequence_logger import SequenceLogger

from rai_python_harness.utils import cell_has_inputs, open_file, sanitize_query_name


@dataclass
class Sequence:
    context: api.Context
    schema: Schema
    sequence_logger: SequenceLogger
    database: str = None
    engine: str = None
    # Non-initialized variables are bound "in post" to accommodate CLI args
    # _engine: str = field(init=False)
    # _database: str = field(init=False)
    _data_dir: Path = field(init=False)
    _source_dir: Path = field(init=False)

    def __post_init__(self):
        # Bind variables to CLI args (highest rank) or contents of TOML file (default)
        # self.engine = self.schema.get("engine")
        # self.database = self.schema.get("database")
        self.data_dir = Path(
            self.schema.toml_path.parent / self.schema.get("data_dir")
        ).absolute()
        self.source_dir = Path(
            self.schema.toml_path.parent / self.schema.get("source_dir")
        ).absolute()

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
    def engine(self) -> str:
        return self._engine

    @engine.setter
    def engine(self, name: str) -> None:
        self._engine = name

    @property
    def source_dir(self) -> Path:
        return self._source_dir

    @source_dir.setter
    def source_dir(self, path: Path) -> None:
        self._source_dir = path

    def exec(self) -> None:
        """Execute each cell in `schema.query` using `schema.get("engine")` in the database `schema.get("database")`."""

        # Iterate 'queries' array and dispatch queries entry-by-entry
        for qry in self.schema.get("queries"):
            # Generate a 'sanitized' name for query
            query_name = sanitize_query_name(qry)

            self.sequence_logger.info(
                f"{qry['index']}: {query_name} ({qry['type'].upper()})"
            )

            # Assign path for source file
            if qry["type"] == "data" and ("inputs" not in qry):
                source_path = Path(self.data_dir / qry["file_path"])
            else:
                source_path = Path(self.source_dir / qry["file_path"])

            self.sequence_logger.info(f"Attempting to load '{source_path}'")
            try:
                source = open_file(source_path)
            except FileNotFoundError:
                self.sequence_logger.err(f"'{source_path}' not found, exiting")
                exit()

            inputs = None
            if cell_has_inputs(qry):
                self.sequence_logger.info(
                    "Create 'inputs' dictionary (as necessary)..."
                )

                inputs = {
                    key: open_file(Path(self.data_dir / value))
                    if Path(self.data_dir / value).is_file()
                    else value
                    for entry in qry["inputs"]
                    for key, value in entry.items()
                }

            # Variable to hold results of query operation
            result = None

            query_type_uppercase = qry["type"].upper()

            # Dispatch based on query type
            if query_type_uppercase in ["QUERY", "UPDATE"]:
                self.sequence_logger.info(f"Running {qry['type']}...")
                result = api.exec(
                    self.context,
                    self.database,
                    self.engine,
                    source,
                    inputs=inputs,
                    # "UPDATE" != "UPDATE" => `False`
                    readonly=(query_type_uppercase != "UPDATE"),
                )
            elif query_type_uppercase == "INSTALL":
                self.sequence_logger.info("Bundling model(s)...")
                model = {}
                model[f"{source_path.name.replace('.rel', '')}"] = source

                self.sequence_logger.info("Installing model(s)...")
                result = api.install_model(
                    self.context, self.database, self.engine, model
                )
            elif query_type_uppercase == "DATA":
                self.sequence_logger.info(f"Loading data...")
                file_path_suffix = Path(qry["file_path"]).suffix

                result = data_query(
                    self.context,
                    self.database,
                    self.engine,
                    inputs,
                    source,
                    query_name,
                    self.sequence_logger,
                    (
                        file_path_suffix
                        if (file_path_suffix in [".csv", ".json"])
                        else None
                    ),
                )
            else:
                self.sequence_logger.warn(
                    f"Query type {qry['type']} not recognized, skipping..."
                )

            log_result(result, qry["index"], query_name, self.sequence_logger)

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
