from pytomlpp import load as tomload

try:
    schema = tomload("schema.toml")
except:
    exit(
        "'schema.toml' contains an error or was not found in root of current directory"
    )

# try:
#     validate(schema)
# except Exception as e:
#     exit(f"EXCEPTION: {e}")


from functools import reduce

from json import dumps as json_dumps
from pandas import DataFrame
from pathlib import Path
from railib import api, config
from time import localtime, strftime

import logging

# Generate timestamp for run
current_time_str = strftime("%Y-%m-%dT%H%M%S", localtime())

# "Reset" `output/`
output_dir = Path(Path.cwd() / "output")

# Rename 'output/', if it exists
if output_dir.exists():
    output_dir.rename(Path.cwd() / f"output-{current_time_str}")

output_dir.mkdir(parents=False, exist_ok=False)

# Initiate logger
logging.basicConfig(datefmt="%Y-%m-%dT%H%M%S.%.3f")
log_file_path = f"output/{current_time_str}-{schema['project']}.log"
log_file_handler = logging.FileHandler(log_file_path)
log_file_handler.setLevel(logging.DEBUG)

logger = logging.getLogger(log_file_path)
logger.setLevel(logging.DEBUG)
logger.addHandler(log_file_handler)

# Set RAI variables for connection
con = api.Context(**config.read())

# Create database if requested
if schema["create_database"]:
    try:
        api.delete_database(con, schema["database"])
    except:
        print("No database present.")

    print(f"Creating database '{schema['database']}'")
    api.create_database(con, schema["database"], schema["engine"], overwrite=True)

#
# Functions for running and logging operations on RelationalAI
#
def dispatch_operation(cell: dict, ctx: api.Context, database: str, engine: str):
    if "file" in cell:
        source_path = f"{schema['source_dir']}{cell['file']}"
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
        )
    elif cell["type"] == "UPDATE":
        run_query_log_result(
            ctx,
            database,
            engine,
            source,
            f"{cell['index']}-{source_path.replace('/', '-')}",
            read_only=False,
            return_df=False,
        )
    elif cell["type"] == "INSTALL":
        install_model_log_result(
            ctx,
            database,
            engine,
            {f"notebooks/{source_path.replace('.rel', '')}": source},
            f"{cell['index']}-{source_path.replace('/', '-')}",
            cell["index"],
        )
    elif cell["type"] == "DATA":
        # read data files in `cell["inputs"]`
        if "inputs" in cell and len(cell["inputs"]) > 0:
            inputs = {k: read_cell(v) for npt in cell["inputs"] for k, v in npt.items()}

            run_query_log_result(
                ctx,
                database,
                engine,
                source,
                f"{cell['index']}-{source_path.replace('/', '-')}",
                read_only=False,
                inputs=inputs,
                return_df=False,
            )
        else:
            load_file_log_results(
                ctx,
                database,
                engine,
                schema["data_path"],
                cell["relation_name"],
                # { "schema": cell["schema"] } if "schema" in cell else {} # NOT YET SUPPORTED BY SDK
            )
    else:
        logger.error(f"ERROR: KEY '{cell['type']}' NOT SUPPORTED", exc_info=True)


def install_model_log_result(
    ctx: api.Context, db: str, engine: str, models: dict, file_path: str, index: int
):
    result = None

    logger.info(f"INSTALLING {index}-{','.join(models.keys())}")
    try:
        result = api.install_model(ctx, db, engine, models)
    except Exception as e:
        logger.error(f"EXCEPTION: {e}", exc_info=True)

    if result:
        if len(result["problems"]) > 0:
            logger.info("PROBLEMS")
        else:
            logger.info("SUCCESS")

        # strip extension
        file_path_no_ext = Path(f"output/{file_path}").with_suffix("")

        write_result(f"{file_path_no_ext}.json", json_dumps(result))
        logger.info(f"JSON output written to '{file_path_no_ext}.json'")
    else:
        logger.error("ERROR: Result is empty", exc_info=True)


# TODO Add `syntax` when available
def load_file_log_results(
    ctx: api.Context, db: str, engine: str, data_path: str, rel_name: str
):
    logger.info(f"LOADING {data_path} to {db}:{rel_name}...", exc_info=True)
    try:
        data = read_cell(data_path)

        if f.suffix == ".csv":
            # TODO Add `syntax` when available
            result = api.load_csv(ctx, db, engine, rel_name, data)
        elif f.suffix == ".json":
            result = api.load_json(ctx, db, engine, rel_name, data)
        else:
            raise Exception(f"File format '{f.suffix}' not supported.")

        if result:
            if len(result["problems"]) > 0:
                logger.info("PROBLEMS", exc_info=True)
            else:
                logger.info("SUCCESS", exc_info=True)
    except Exception as e:
        logger.error(f"EXCEPTION: {e}", exc_info=True)


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
    file_path: str,
    read_only: bool = True,
    inputs: dict = {},
    return_df: bool = True,
):
    result = None

    logger.info(f"RUNNING {file_path}", exc_info=True)
    try:
        result = (
            api.query(ctx, db, engine, qry, readonly=read_only, inputs=inputs)
            if inputs
            else api.query(ctx, db, engine, qry, readonly=read_only)
        )

        if result:
            if len(result["problems"]) > 0:
                logger.info("PROBLEMS", exc_info=True)
            else:
                logger.info("SUCCESS", exc_info=True)

            # strip extension
            file_path_no_ext = Path(f"output/{file_path}").with_suffix("")

            # write CSV if requested
            if return_df:
                to_DF(result, return_df=return_df).to_csv(f"{file_path_no_ext}.csv")
                logger.info(f"CSV written to '{file_path_no_ext}.csv", exc_info=True)

            # write and log results
            write_result(f"{file_path_no_ext}.json", json_dumps(result))
            logger.info(
                f"JSON output written to '{file_path_no_ext}.json'", exc_info=True
            )
        else:
            raise Exception("Result is empty.")
    except Exception as e:
        logger.error(f"EXCEPTION: {e}", exc_info=True)


# TODO: Complete function
# def validate(schema: dict):
#     # validate schema...
#     if not ok:
#         return Exception("Schema does not validate.")


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
for query in schema["queries"]:
    query["type"] = query["type"].upper()
    dispatch_operation(query, con, schema["database"], schema["engine"])
