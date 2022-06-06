# RelationalAI Standalone Run Harness for `rai-sdk-julia`
Deterministic and "standalone" run harness for Rel projects; uses [TOML][tomlio] files for configuration and the [RAI Julia SDK][raisdkjulia] to transact with RelationalAI's KGMS. Execution sequences may be defined entirely within a TOML configuration then executed via `harness.jl` as described below.

## Setup and Execution
1. Edit TOML configuration(s) as needed (see below)
1. Ensure you have `~/.rai/config` properly configured
   - See [Create a configuration file](https://github.com/relationalai/rai-sdk-julia#create-a-configuration-file) from the Julia SDK
1. Install `rai-sdk-julia`
   - `julia harness/install_dependencies.jl`
   - [Installation instructions](https://github.com/RelationalAI/rai-sdk-julia#installation)
1. Execute with `julia harness.jl </path/to/{config}.toml>`
   1. Results written to `</path/to/{config}.toml>/output-{config}/`, directory is preseved by future operations
   
## TOML Configuration Files
`run_harness.py` provides some validation for Configuration files. See [toml.io][tomlio] for description of format.

| Key                             | Type            | Description                                                                                                | Required?                                      |
|:--------------------------------|:---------------:|:-----------------------------------------------------------------------------------------------------------|:----------------------------------------------:|
| `authors`                       | `Array<String>` | Project/script authors and contributors                                                                    | `Y`                                            |
| `create_database`               | `Boolean`       | Delete then create new database on run                                                                     | `Y`                                            |
| `data_dir`                      | `String`        | Path to data directory, default is `data/`                                                                 | `Y`                                 |
| `database`                      | `String`        | Name RAI of database to use                                                                                | `Y`                                            |
| `description`                   | `String`        | Information on project/script for others' reference                                                        | `Y`                                            |
| `engine`                        | `String`        | Name of RAI engine to use                                                                                  | `Y`                                            |
| `project`                       | `String`        | Project configuration belongs to                                                                           | `Y`                                            |
| `source_dir`                    | `String`        | Path to `*.rel` files, default is `src/`                                                                   | `Y`                                            |
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

## Punch List
- [ ] Cloud path compatibility
  - [ ] Azure (public)
    - [ ] Credentials (private)
  - [ ] S3 (public)
- [ ] Complete `README`
- [ ] Runnable `example/`
  - [ ] Loads data
    - [ ] `load_csv`
    - [ ] `load_json`
    - [ ] `update`
  - [ ] Installs models
  - [ ] Runs queries
    - [ ] Queries
    - [ ] Tests
- [ ] Logs run operations
  - [ ] via `Logging`
  - [ ] Writes return packets to disk
- [ ] Dispatches operations by `type` (sepcified in `{config}.toml` `queries`)
- [x] Initiates `output-{config}/` adjacent to `{config}.toml`
  - [x] Renames existing directory, if necessary
- [x] Allows specification options via CLI
  - [x] `arg` validation
  - [x] `config` file path
  - [x] `--database` to use (RAI Cloud)
  - [x] `--engine` to use (RAI Cloud)
  - [x] `--profile` to use (RAI Cloud)
- [x] Configuration schema validation

[raiinputs]: https://docs.relational.ai/rkgms/sdk/julia-sdk#specifying-inputs
[raisdkjulia]: https://github.com/RelationalAI/rai-sdk-julia
[tomlio]: https://toml.io/
