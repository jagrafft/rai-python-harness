from __future__ import annotations

from pathlib import Path
from pytomlpp import load


def load_toml_or_exit(toml_path) -> dict:
    """Load TOML file with `pytomlpp.load`, or fail"""
    try:
        return load(toml_path)
    except:
        exit(
            f"EXECUTION STOPPED: Error loading '{schema_path}'. TOML file may contain an error (try a linter) or was not found."
        )


def valid_file_extension_or_exit(schema_path: Path, ext) -> None:
    """Checks the suffix to determines if `schema_path` matches the expected file extension. Fails when match is `False`."""
    if schema_path.suffix != ext:
        exit(
            f"EXECUTION STOPPED: Extension of '{schema_path}' is '{schema_path.suffix}'; must be '.toml'"
        )


def valid_schema_or_exit(schema_path: Path) -> dict:
    """Validate TOML schema or fail trying."""

    # File extension (suffix) is ".toml", or fail
    valid_file_extension_or_exit(schema_path, ".toml")

    # Load TOML file or fail
    schema = load_toml_or_exit(schema_path)

    REQUIRED_KEYS = {
        "global": [
            "authors",
            "engine",
            "create_database",
            "data_dir",
            "database",
            "description",
            "project",
            "source_dir",
        ],
        "queries": [
            "file_path",
            "index",
            "type",
        ],
    }

    # Check for presence of required keys
    for key in REQUIRED_KEYS["global"]:
        if key not in schema:
            exit(f"EXECUTION STOPPED: Configuration file must have key '{key}'")

    # Validate 'version_control' Table
    if "version_control" in schema:
        if "url" in schema["version_control"]:
            if len(schema["version_control"]["url"]) == 0:
                exit("EXECUTION STOPPED: Version control URL may not be empty")
        else:
            exit(
                f"EXECUTION STOPPED:The 'version_control' entry in '{schema_path}' must have 'url' key"
            )
    else:
        exit(
            f"EXECUTION STOPPED: '{schema_path}' must have 'version_control' entry (Table)"
        )

    # Ensure configuration file has 'queries' array, and it has
    # at least one (1) entry
    if "queries" in schema:
        if len(schema["queries"]) == 1 and schema["queries"][0] == {}:
            exit("EXECUTION STOPPED: 'queries' array may not be empty")
    else:
        exit(f"EXECUTION STOPPED: '{schema_path}' must have a 'queries' array")

    # Ensure indices of elements in 'queries' array are unique
    indices = [qry["index"] for qry in schema["queries"]]

    if len(indices) != len(set(indices)):
        exit(f"EXECUTION STOPPED: Duplicate keys in '{schema_path}'")

    # Ensure entries in 'queries' array have required keys
    for query in schema["queries"]:
        for key in REQUIRED_KEYS["queries"]:
            if key not in query:
                exit(f"EXECUTION STOPPED: query {query['index']} must have key '{key}'")

    # Ensure 'data' entries without an 'input' key have the key 'name'
    data_queries_without_input_key = [
        qry
        for qry in schema["queries"]
        if (qry["type"].upper() == "DATA") and ("inputs" not in qry)
    ]

    for data_query in data_queries_without_input_key:
        if "name" not in data_query:
            exit(
                f"EXECUTION STOPPED: data query {query['index']} does not have an 'inputs' key so it must have a 'name' key"
            )

    # Validation checks passed
    return schema
