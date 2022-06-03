from pathlib import Path
from sys import argv

# Verify CLI input is valid
if len(argv) == 2:
    toml_path = Path(argv[1])
    if toml_path.suffix != ".toml":
        print(f"{toml_path}'s extension is '{toml_path.suffix}', must be '.toml'")
else:
    print("\nERROR: Script takes a single (1) argument")
    print("Usage: run_harness.py </path/to/{config}>.toml")
    exit()

# Load TOML configuration
from pytomlpp import load as tomload

try:
    config = tomload(toml_path)
except:
    exit(
        "'config.toml' contains an error or was not found in root of current directory"
    )


# Validates TOML configuration
# TODO Relocate
def validate(schema: dict):
    required_keys = {
        "global": [
            "authors",
            "create_database",
            "data_dir",
            "database",
            "description",
            "engine",
            "project",
            "source_dir",
        ],
        "queries": [
            "file_name",
            "index",
            "type",
        ],
    }

    # Check for presence of required keys
    for key in required_keys["global"]:
        if key not in schema:
            exit(f"ERROR: Configuration file must have key '{key}'")

    # Validate 'version_control' Table
    if "version_control" in schema:
        if "url" in schema["version_control"]:
            if len(schema["version_control"]["url"]) == 0:
                exit("ERROR: Version control URL may not be empty")
        else:
            exit("ERROR: 'version_control' must have 'url' key")
    else:
        exit("ERROR: Configuration file must have 'version_control' entry (Table)")

    # Ensure configuration file has 'queries' array, and it is full
    if "queries" in schema:
        if len(schema["queries"]) == 1 and schema["queries"][0] == {}:
            exit("ERROR: 'queries' array may not be empty")
    else:
        exit("ERROR: Configuration file must have 'queries' array")

    # Ensure indices of 'queries' array are monotonic
    indices = [qry["index"] for qry in schema["queries"]]

    if len(indices) != len(set(indices)):
        exit("ERROR: Duplicate keys in configuration file")

    # Ensure entries in 'queries' array have required keys
    for query in schema["queries"]:
        for key in required_keys["queries"]:
            if key not in query:
                exit(f"ERROR: query {query['index']} must have key '{key}'")


# Validate TOML configuration
validate(config)


# Configuration files are valid, continue with execution
from functools import reduce

from json import dumps as json_dumps
from pandas import DataFrame
from railib import api, config as rai_config
from time import localtime, strftime

import logging

# Generate timestamp for run
current_time_str = strftime("%Y-%m-%dT%H%M%S", localtime())

# "Reset" `output/`
output_dir = Path(toml_path.parent.resolve() / f"output-{toml_path.stem}")

print(f"output_dir: {output_dir}")
# Rename 'output/', if it exists
if output_dir.exists():
    output_dir.rename(f"{output_dir}-{current_time_str}")

output_dir.mkdir(parents=False, exist_ok=False)

# Initiate logger
logging.basicConfig(datefmt="%Y-%m-%dT%H%M%S.%.3f")
log_file_path = Path(output_dir / f"{current_time_str}-{config['project']}.log")
log_file_handler = logging.FileHandler(log_file_path)
log_file_handler.setLevel(logging.DEBUG)

logger = logging.getLogger(f"{log_file_path}")
logger.setLevel(logging.DEBUG)
logger.addHandler(log_file_handler)

# Set RAI variables for connection
con = api.Context(**rai_config.read())

# Create database if requested
if config["create_database"]:
    try:
        api.delete_database(con, config["database"])
    except:
        print("No database present.")

    print(f"Creating database '{config['database']}'")
    api.create_database(con, config["database"], config["engine"], overwrite=True)

#
# Functions for running and logging operations on RelationalAI
#
def dispatch_operation(cell: dict, ctx: api.Context, database: str, engine: str):
    source = None

    if "file_name" in cell:
        # Use `Path` to ensure proper construction
        dir_to_use = (
            config["data_dir"] if "relation_name" in cell else config["source_dir"]
        )

        _source_path = Path(toml_path.parent / dir_to_use / cell["file_name"])
        # Convert `Path` to string for "downstream" use
        source_path = f"{_source_path}"

        try:
            source = read_cell(source_path)
        except Exception as e:
            logger.error(f"EXCEPTION: {e}", exc_info=True)
            logger.error(f"Cannot read from {source_path}.", exc_info=True)

    if cell["type"] == "QUERY":
        run_query_log_result(
            ctx,
            database,
            engine,
            source,
            f"{cell['index']}-{source_path.replace('/', '-')}",
            index=cell["index"],
        )
    elif cell["type"] == "UPDATE":
        run_query_log_result(
            ctx,
            database,
            engine,
            source,
            Path(output_dir / f"{cell['index']}-{cell['file_name']}"),
            read_only=False,
            return_df=False,
            index=cell["index"],
        )
    elif cell["type"] == "INSTALL":
        install_model_log_result(
            ctx,
            database,
            engine,
            {f"notebooks/{source_path.replace('.rel', '')}": source},
            Path(output_dir / f"{cell['index']}-{cell['file_name']}"),
            cell["index"],
        )
    elif cell["type"] == "DATA":
        project_data_dir = Path(toml_path.parent.resolve() / config["data_dir"])
        print(f"project_data_dir: {project_data_dir}")

        # read data files in `cell["inputs"]`
        if "inputs" in cell and len(cell["inputs"]) > 0:
            inputs = {
                k: read_cell(f"{project_data_dir}/{v}")
                for npt in cell["inputs"]
                for k, v in npt.items()
            }

            run_query_log_result(
                ctx,
                database,
                engine,
                source,
                Path(output_dir / f"{cell['index']}-{cell['file_name']}"),
                read_only=False,
                inputs=inputs,
                return_df=False,
                index=cell["index"],
            )
        else:
            load_file_log_results(
                ctx,
                database,
                engine,
                source,
                Path(output_dir / f"{cell['index']}-{cell['file_name']}"),
                cell["relation_name"],
                # { "config": cell["config"] } if "config" in cell else {} # NOT YET SUPPORTED BY SDK
                index=cell["index"],
            )
    else:
        logger.error(f"ERROR: KEY '{cell['type']}' NOT SUPPORTED", exc_info=True)


def install_model_log_result(
    ctx: api.Context, db: str, engine: str, models: dict, file_path: Path, index: int
):
    logger.info(f"INSTALLING {index}-{','.join(models.keys())}")
    try:
        result = api.install_model(ctx, db, engine, models)
    except Exception as e:
        logger.error(f"EXCEPTION: {e}", exc_info=True)
        logger.error("ERROR: Could not install model")

    if result:
        if len(result["problems"]) > 0:
            logger.info("PROBLEMS")
        else:
            logger.info("SUCCESS")

        # strip extension
        file_path_no_ext = file_path.with_suffix("")

        write_result(f"{file_path_no_ext}.json", json_dumps(result))
        logger.info(f"JSON output written to '{file_path_no_ext}.json'")
    else:
        logger.error("ERROR: Result is empty", exc_info=True)


# TODO Add `syntax` when available
def load_file_log_results(
    ctx: api.Context,
    db: str,
    engine: str,
    data: str,
    file_path: Path,
    rel_name: str,
    syntax: dict = {},
    index: int = 0,
):
    logger.info(
        f"LOADING {index}-{file_path.name} to {db}:{rel_name}...", exc_info=True
    )
    if file_path.suffix == ".csv":
        # TODO Add `syntax` when available
        result = api.load_csv(ctx, db, engine, rel_name, data)
    elif file_path.suffix == ".json":
        result = api.load_json(ctx, db, engine, rel_name, data)
    else:
        logger.error(f"File format '{file_path.suffix}' not supported.")

    if result:
        if len(result["problems"]) > 0:
            logger.info("PROBLEMS", exc_info=True)
        else:
            logger.info("SUCCESS", exc_info=True)

        # strip extension
        file_path_no_ext = file_path.with_suffix("")

        write_result(f"{file_path_no_ext}.json", json_dumps(result))
        logger.info(f"JSON output written to '{file_path_no_ext}.json'")
    else:
        logger.error("ERROR: Could not write results")


def read_cell(path: str) -> str:
    _cell = open(path, "r")
    cell = _cell.read()
    _cell.close()
    return cell


def run_query_log_result(
    ctx: api.Context,
    db: str,
    engine: str,
    qry: str,
    file_path: Path,
    read_only: bool = True,
    inputs: dict = {},
    return_df: bool = True,
    index: int = 0,
):
    result = None

    logger.info(f"RUNNING {index}-{file_path.name}", exc_info=True)
    try:
        result = (
            api.query(ctx, db, engine, qry, readonly=read_only, inputs=inputs)
            if inputs
            else api.query(ctx, db, engine, qry, readonly=read_only)
        )
    except Exception as e:
        logger.error(f"EXCEPTION: {e}", exc_info=True)
        logger.error("ERROR: Could not fetch result")

    if len(result["problems"]) > 0:
        logger.info("PROBLEMS", exc_info=True)
    else:
        logger.info("SUCCESS", exc_info=True)

    # strip extension
    file_path_no_ext = file_path.with_suffix("")

    # write CSV if requested
    if return_df:
        to_DF(result, return_df=return_df).to_csv(f"{file_path_no_ext}.csv")
        logger.info(f"CSV written to '{file_path_no_ext}.csv", exc_info=True)

    # write and log results
    write_result(f"{file_path_no_ext}.json", json_dumps(result))
    logger.info(f"JSON output written to '{file_path_no_ext}.json'", exc_info=True)


def write_result(file_path: str, contents: str):
    outfile = open(file_path, "wb")
    outfile.write(bytes(contents, "utf-8"))
    outfile.close()


#
# Utilities for converting query results to a Pandas DataFrame
#
def to_DF(rel, columns=None, return_df=True):
    """
    Invoke `single_key_relation_to_DF` or `multi_key_relation_to_DF` based on length of
    `output` key in dictionary returned from RAI.
    """
    return (
        single_key_relation_to_DF(rel, return_df, columns=columns)
        if len(rel["output"]) == 1
        else multikey_relation_to_DF(rel, return_df)
    )


def multikey_relation_to_DF(rel, return_df):
    """
    Transform a multikey relation with a 'ragged right' structure (e.g. not all relations
    are the same cardinality) to a Pandas `DataFrame` (default) or Python `dict`.
    NB. Function fills 'missing' keys in each relation with the value `None`.
    """

    # Traverse all `dict`s in the `output` array and add the contents of
    # the first index of `columns`--the keys for our data--to a `set`.
    global_key_set = set(
        reduce(lambda X, Y: X + Y, [x["columns"][0] for x in rel["output"]])
    )

    # Used in the `for` loop below
    data = {}

    # Traverse all `dict`s in the `output` array (again) and insert `None` values
    # for missing keys in each relation.
    for X in rel["output"]:
        # Create a `dict` of key-value pairs for the data included in the current relation.
        key_value_pairs = {
            x: X["columns"][1][i] for (i, x) in enumerate(X["columns"][0])
        }

        """
        Create key in `data` to store 'polyfilled' relation (e.g. relation with `None`s) then
        iterate `global_key_set` and check whether each of its members is included in `key_value_pairs`.
        Rules
            YES => insert value associated with key
            NO  => insert `None`
        """
        data[X["rel_key"]["keys"][0].replace(":", "")] = [
            key_value_pairs[k] if k in key_value_pairs else None for k in global_key_set
        ]

    # Return a Pandas `DataFrame` or Python `dict`
    return DataFrame(data) if return_df else data


def single_key_relation_to_DF(rel, return_df, columns=None):
    """
    Transform a single key relation to a Pandas `DataFrame` or Python `dict`.
    """
    if columns is not None:
        # If user provided column names, ensure there are exactly enough for available data relations.
        if len(columns) != len(rel["output"][0]["columns"]):
            logger.error(
                "ERROR: Length of 'columns' != number of columns in data.",
                exc_info=True,
            )
            exit()
        else:
            d = {columns[i]: v for (i, v) in enumerate(rel["output"][0]["columns"])}

            # Return `DataFrame` or `dict` of key-value pairs where keys populate from `columns`.
            return DataFrame(d) if return_df else d
    else:
        d = {f"x{i}": v for (i, v) in enumerate(rel["output"][0]["columns"])}

        # Return `DataFrame` or `dict` of key-value pairs where keys are generated automatically.
        return DataFrame(d) if return_df else d


#
# RUN LOOP
#
for query in config["queries"]:
    query["type"] = query["type"].upper()
    dispatch_operation(query, con, config["database"], config["engine"])
