# RelationalAI Python Run Harness
Deterministic run harness for Rel projects. Execution sequences are defined in [TOML][tomlio] files then executed using RAI's [Python SDK][raisdkpython]. Harness provides basic logging and programmatic control for executing one or more sequences in a predictable manner.

## Setup and Execution
1. Install Python [Poetry][pypoetry]
1. Edit TOML configuration(s) as needed (see below)
1. Ensure you have `~/.rai/config` properly configured
   - See [Create a configuration file](https://github.com/relationalai/rai-sdk-python#create-a-configuration-file) from the Python SDK
   - You may customize the `config` path, and other parameters, via the run harness' command-line functionality
1. Enter the directory
   1. `cd rai-python-harness`
1. If needed, initialize the Poetry virtual environment
   1. `poetry install`
1. See `tests/` for usage examples
   - **Some tests require RAI Cloud credentials**
   
## TOML Execution Sequence Files
- Harness provides validation for Configuration files
- See [toml.io][tomlio] for description of format
- A [TOML Linter][tomlint] will likely save you time debugging

| Key                         | Type           | Description                                                                                                | Required?                     |
|:----------------------------|:--------------:|:-----------------------------------------------------------------------------------------------------------|:-----------------------------:|
| `data_dir`                  | `String`       | Path to data directory, default is `data/`                                                                 | `Y`                           |
| `source_dir`                | `String`       | Path to `*.rel` files                                                                                      | `Y`                           |
| `queries`                   | `Array<Table>` | Array with a `Table` to describe how each operation should be executed                                     | `Y`                           |
| `queries.<Table>.file_path` | `String`       | Path to `*.rel` file from _within_ `source_dir` (e.g. `${source_dir}/data_load.rel => data_load.rel`)      | `ALL queries`                 |
| `queries.<Table>.index`     | `Integer`      | Rank of operation, with zero (`0`) being first. Each `index` must be _unique and monotonically increasing_ | `ALL queries`                 |
| `queries.<Table>.inputs`    | `Table`        | `Table` of `key-value` pairs for input substitution, see [specifying inputs][raiinputs]                    | `DATA queries` using `update` |
| `queries.<Table>.name`      | `String`       | Name of relation                                                                                           | `ALL queries`                 |
| `queries.<Table>.type`      | `String`       | Type of operation, see below                                                                               | `ALL queries`                 |

### Operation Types
| Type      | Description                                                                                                                                        |
|:---------:|:---------------------------------------------------------------------------------------------------------------------------------------------------|
| `DATA`    | Push data from files to a RAI database. There are two (2) data query subtypes, differentiated by the keys `inputs` and `relation_name` (see below) |
| `INSTALL` | Install a model to a RAI database                                                                                                                  |
| `QUERY`   | Run a query against the specified RAI database using the specified engine                                                                          |
| `UPDATE`  | Run an `update` query against the specified RAI database using the specified engine. `update` operations _modify data_                             |

#### `DATA` query subtypes
| Query       | Description                                                                                                                                        |
|:------------|:---------------------------------------------------------------------------------------------------------------------------------------------------|
| `load_csv`  | Ensure `Table` entry in TOML configuration includes ONLY the allowed keys, harness will determine file extension and call correct utility.         |
| `load_json` | Ensure `Table` entry in TOML configuration includes ONLY the allowed keys, harness will determine file extension and call correct utility.         |
| `update`    | Ensure `Table` entry in TOML configuration includes ONLY the allowed keys, and that the `keys` of the `inputs` `Table` match keys in the Rel file. |

[pypoetry]: https://python-poetry.org/
[raiinputs]: https://docs.relational.ai/rkgms/sdk/python-sdk#specifying-inputs
[raisdkjulia]: https://github.com/RelationalAI/rai-sdk-julia
[raisdkpython]: https://github.com/RelationalAI/rai-sdk-python
[tomlint]: https://www.toml-lint.com/
[tomlio]: https://toml.io/
