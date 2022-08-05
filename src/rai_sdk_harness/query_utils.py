from __future__ import annotations

from json import dumps
from pathlib import Path
from railib import api
from typing import Union

from rai_sdk_harness.sequence_logger import SequenceLogger


def data_query(
    context: api.Context,
    inputs: Union[None, dict],
    source: str,
    name: str,
    logger: SequenceLogger,
):
    result = None

    if inputs:
        # Use update query if `inputes` is not `None`
        result = api.query(
            self.context,
            self.database,
            self.compute,
            query_source,
            readonly=False,
            inputs=inputs,
        )
    else:
        # Use `api.load_csv` or `api.load_json` depending on file extension
        load_fn = None

        if query_path.suffix == ".csv":
            logger.info("CSV file, using `api.load_csv`...")
            load_fn = api.load_csv
        elif query_path.suffix == ".json":
            logger.info("JSON file, using `api.load_json`...")
            load_fn = api.load_json
        else:
            logger.warn(f"File type '{query_path.suffix}' not supported, skipping...")

        if load_fn:
            result = load_fn(
                self.context,
                self.database,
                self.compute,
                name,
                source,
            )

    return result


def log_result(result, index: int, query_name: str, logger: SequenceLogger):
    if result:
        if len(result["problems"]) > 0:
            logger.warn("PROBLEMS")
            logger.warn(
                f"`result['problems']` non-empty (length {len(result['problems'])})"
            )
        else:
            logger.info("SUCCESS")

        write_file(Path(logger.log_output_dir / f"{index}-{query_name}.json"))
    else:
        logger.err("ERROR")
        logger.err("`result` is empty")
