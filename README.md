# RelationalAI Standalone Run Harness for `rai-sdk-python`
Deterministic and "standalone" run harness for Rel projects; uses [TOML][tomlio] files for configuration and the [RAI Python SDK][raisdkpython] to transact with RelationalAI's KGMS. Execution sequences may be defined entirely within a TOML configuration then executed via `run_harness.py` as described below.

## Setup and Execution
1. Edit TOML configuration(s) as needed (see below)
1. Ensure you have `~/.rai/config` properly configured
   - See [Create a configuration file](https://github.com/relationalai/rai-sdk-python#create-a-configuration-file) from the Python SDK
   - You may customize the `config` path by editing `run_harness.py`
1. If needed, create a virtual environment
   1. `python3 -m venv rai-python-harness/`
   1. `source rai-python-harness/bin/activate`
   1. `cd rai-python-harness/`
   1. `pip install -r requirements.txt`
1. Execute with `python3 run_harness.py </path/to/{config}.toml>`
   1. Results written to `output-{config}/`, directory is preseved by future operations
   
## TOML Configuration Files
See [toml.io][tomlio] for description of format.

| Key                             | Type            | Description                                                                                                | Required?                                      |
|:--------------------------------|:---------------:|:-----------------------------------------------------------------------------------------------------------|:----------------------------------------------:|
| `authors`                       | `Array<String>` | Project/script authors and contributors                                                                    | `Y`                                            |
| `create_database`               | `Boolean`       | Delete then create new database on run                                                                     | `Y`                                            |
| `data_dir`                      | `String`        | Path to data directory                                                                                     | `DATA queries`                                 |
| `database`                      | `String`        | Name RAI of database to use                                                                                | `Y`                                            |
| `description`                   | `String`        | Information on project/script for others' reference                                                        | `Y`                                            |
| `engine`                        | `String`        | Name of RAI engine to use                                                                                  | `Y`                                            |
| `project`                       | `String`        | Project configuration belongs to                                                                           | `Y`                                            |
| `source_dir`                    | `String`        | Path to `*.rel` files                                                                                      | `Y`                                            |
| `version_control`               | `Table`         | `Table` (`Hash`/`Dictionary`) with information on version control                                          | `Y`                                            |
| `version_control.url`           | `String`        | Path to repository for version control                                                                     | `Y`                                            |
| `queries`                       | `Array<Table>`  | Array with a `Table` to describe how each operation should be executed                                     | `Y`                                            |
| `queries.<Table>.file_name`     | `String`        | Name of file to load                                                                                       | `ALL queries`                                  |
| `queries.<Table>.index`         | `Integer`       | Rank of operation, with zero (`0`) being first. Each `index` must be _unique and monotonically increasing_ | `ALL queries`                                  |
| `queries.<Table>.inputs`        | `Table`         | `Table` of `key-value` pairs for input substitution, see [specifying inputs][raiinputs]                    | `DATA queries` using `update`                  |
| `queries.<Table>.note`          | `String`        | Intended to concise descriptions                                                                           |                                                |
| `queries.<Table>.notes`         | `Table`         | `key-value` pair(s) intended for more robust documentation                                                 |                                                |
| `queries.<Table>.relation_name` | `String`        | Name of relation                                                                                           | `DATA queries` using `load_csv` or `load_json` |
| `queries.<Table>.type`          | `String`        | Type of operation, see below                                                                               | `ALL queries`                                  |

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

### Notes
1. Specify directory with `*.rel` files using the `source_dir` key
   - Default value is `src/`
1. Specify data directory using the `data_dir` key

## Punch List
- [ ] Cloud path compatibility
  - [ ] Azure (public)
    - [ ] Credentials (private)
  - [ ] S3 (public)
- [ ] Configuration schema validation
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
- [x] Allows specification of configuration file via CLI
  - [x] CLI option with `arg` validation
  - [x] `Path`s "anchor" to location of specified configuration
  - [x] Update `output/` path, and path relocation

[raiinputs]: https://docs.relational.ai/rkgms/sdk/python-sdk#specifying-inputs
[raisdkpython]: https://github.com/RelationalAI/rai-sdk-python
[tomlio]: https://toml.io/
