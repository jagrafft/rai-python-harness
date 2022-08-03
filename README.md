# RelationalAI Standalone Run Harness for `rai-sdk-python`
Deterministic and "standalone" run harness for Rel projects; uses [TOML][tomlio] files for configuration and the [RAI Python SDK][raisdkpython] to transact with RelationalAI's KGMS. Execution sequences may be defined entirely within a TOML configuration then executed via `run_harness.py` as described below.

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
1. Execute (without entering virtual environment) via `poetry run python3 run_harness.py </path/to/{config}.toml>`
   1. Enter virtual environment with `poetry shell`, then issue `python3 run_harness.py </path/to/{config}.toml>`
   1. Results written to `output-{config}/`, directory is preseved by future operations
   
## TOML Configuration Files
`run_harness.py` provides some validation for Configuration files. See [toml.io][tomlio] for description of format.

| Key                        | Type            | Description                                                                                                | Required?                                      |
|:---------------------------|:---------------:|:-----------------------------------------------------------------------------------------------------------|:----------------------------------------------:|
| `authors`                  | `Array<String>` | Project/script authors and contributors                                                                    | `Y`                                            |
| `compute`                  | `String`        | Name of RAI engine to use                                                                                  | `Y`                                            |
| `create_database`          | `Boolean`       | Delete then create new database on run                                                                     | `Y`                                            |
| `data_dir`                 | `String`        | Path to data directory, default is `data/`                                                                 | `Y`                                            |
| `database`                 | `String`        | Name RAI of database to use                                                                                | `Y`                                            |
| `description`              | `String`        | Information on project/script for others' reference                                                        | `Y`                                            |
| `project`                  | `String`        | Project configuration belongs to                                                                           | `Y`                                            |
| `source_dir`               | `String`        | Path to `*.rel` files                                                                                      | `Y`                                            |
| `queries`                  | `Array<Table>`  | Array with a `Table` to describe how each operation should be executed                                     | `Y`                                            |
| `queries.<Table>.index`    | `Integer`       | Rank of operation, with zero (`0`) being first. Each `index` must be _unique and monotonically increasing_ | `ALL queries`                                  |
| `queries.<Table>.inputs`   | `Table`         | `Table` of `key-value` pairs for input substitution, see [specifying inputs][raiinputs]                    | `DATA queries` using `update`                  |
| `queries.<Table>.name`     | `String`        | Name of relation                                                                                           | `DATA queries` using `load_csv` or `load_json` |
| `queries.<Table>.note`     | `String`        | Intended to concise descriptions                                                                           |                                                |
| `queries.<Table>.notes`    | `Table`         | `key-value` pair(s) intended for more robust documentation                                                 |                                                |
| `queries.<Table>.rel_path` | `String`        | Path to `*.rel` file from _within_ `source_dir` (e.g. `${source_dir}/data_load.rel => data_load.rel`)      | `ALL queries`                                  |
| `queries.<Table>.type`     | `String`        | Type of operation, see below                                                                               | `ALL queries`                                  |
| `version_control`          | `Table`         | `Table` (`Hash`/`Dictionary`) with information on version control                                          | `Y`                                            |
| `version_control.url`      | `String`        | Path to repository for version control                                                                     | `Y`                                            |

### Operation Types
| Type      | Description                                                                                                                                        |
|:---------:|:---------------------------------------------------------------------------------------------------------------------------------------------------|
| `DATA`    | Push data from files to a RAI database. There are two (2) data query subtypes, differentiated by the keys `inputs` and `relation_name` (see below) |
| `INSTALL` | Install a model to a RAI database                                                                                                                  |
| `QUERY`   | Run a query against the specified RAI database using the specified engine                                                                          |
| `UPDATE`  | Run an `update` query against the specified RAI database using the specified engine. `update` operations _modify data_                             |

#### `DATA` query subtypes
| Query       | Description                                                                                                                                        | Allowed Keys                                             |
|:------------|:---------------------------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------|
| `load_csv`  | Ensure `Table` entry in TOML configuration includes ONLY the allowed keys, harness will determine file extension and call correct utility.         | `index, type, file_name, queries.schema*, relation_name` |
| `load_json` | Ensure `Table` entry in TOML configuration includes ONLY the allowed keys, harness will determine file extension and call correct utility.         | `index, type, file_name, relation_name`                  |
| `update`    | Ensure `Table` entry in TOML configuration includes ONLY the allowed keys, and that the `keys` of the `inputs` `Table` match keys in the Rel file. | `index, type, file_name, inputs`                         |

## Punch List
- [ ] Cloud path compatibility
  - [ ] Azure (public)
    - [ ] Credentials (private)
  - [ ] S3 (public)
- [ ] Complete `README`
- [ ] Runnable `example/`
  - [x] Loads data
    - [x] `load_csv`
    - [x] `load_json`
    - [x] `update`
  - [ ] Installs models
  - [ ] Runs queries
    - [ ] Queries
    - [ ] Tests
- [ ] Code clean up
  - [ ] Abstraction
  - [ ] Modularization
- [x] Allows specification of configuration file via CLI
  - [x] CLI option with `arg` validation
  - [x] `Path`s "anchor" to location of specified configuration
  - [x] Update `output/` path, and path relocation
- [x] Configuration schema validation

[pypoetry]: https://python-poetry.org/
[raiinputs]: https://docs.relational.ai/rkgms/sdk/python-sdk#specifying-inputs
[raisdkpython]: https://github.com/RelationalAI/rai-sdk-python
[tomlio]: https://toml.io/
