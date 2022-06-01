# RelationalAI Standalone Run Harness for Python

## Setup and Execution
1. Ensure you have `~/.rai/config` properly configured
   - See [Create a configuration file](https://github.com/relationalai/rai-sdk-python#create-a-configuration-file) from the Python SDK
   - You may customize the `config` path by editing `run_harness.py`
1. If needed, create a virtual environment
   1. `python3 -m venv rai-python-harness/`
   1. `source rai-python-harness/bin/activate`
   1. `cd rai-python-harness/`
   1. `pip -r requirements.txt`
1. Edit `schema.toml` as needed (see below)
1. Run harness with `python3 run_harness.py`
   1. Results written to `output/`, directory is preseved by future operations
   
## `schema.toml`

## Directory Structure

## Punch List
- [ ] Schema validation
- [ ] Complete `README`
- [ ] Runnable example
