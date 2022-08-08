from __future__ import annotations

from json import dumps
from pathlib import Path
from railib import api
from typing import Union

from rai_python_harness.sequence_logger import SequenceLogger
from rai_python_harness.utils import write_file


def data_query(
    context: api.Context,
    database: str,
    engine: str,
    inputs: Union[None, dict],
    source: str,
    name: str,
    logger: SequenceLogger,
    file_type: Union[None, str] = None,
):
    result = None
    print(f"file_type: {file_type}")

    if inputs:
        # Use update query if `inputs` is not `None`
        result = api.exec(
            context,
            database,
            engine,
            source,
            inputs=inputs,
            readonly=False,
        )
    else:
        # Use `api.load_csv` or `api.load_json` depending on file extension
        load_fn = None

        if file_type:
            if file_type == ".csv":
                logger.info("CSV file, using `api.load_csv`...")
                load_fn = api.load_csv
            elif file_type == ".json":
                logger.info("JSON file, using `api.load_json`...")
                load_fn = api.load_json
            else:
                logger.warn(f"File type '{file_type}' not supported, skipping...")

        if load_fn:
            result = load_fn(
                context,
                database,
                engine,
                name,
                source,
            )

    return result


def log_result(result, index: int, query_name: str, logger: SequenceLogger):
    _result = dumps(result)

    if _result:
        # TODO: Update to reflect changes in SDK return packet
        # if len(result["problems"]) > 0:
        #     logger.warn("PROBLEMS")
        #     logger.warn(
        #         f"`result['problems']` non-empty (length {len(result['problems'])})"
        #     )
        # else:
        #     logger.info("SUCCESS")

        logger.info("QUERY RETURNED")
        write_file(Path(logger.log_output_dir / f"{index}-{query_name}.json"), _result)
    else:
        logger.err("ERROR")
        logger.err("`result` is empty")
