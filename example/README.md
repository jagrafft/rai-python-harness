# RelationalAI Python Run Harness: Simple Example Project

## Setup and Execution
1. Ensure your [RelationalAI SDK Configuration](https://docs.relational.ai/rkgms/sdk/sdk-configuration) is correct
1. Copy the `example/` directory to desired location and rename as needed
1. Add additional project depedencies to `pyproject.toml`
    - May also edit project name, author, version, et cetera
1. Execute `poetry install` from within directory
1. Set these environment variables (e.g. `export KEY=value`) according to project needs
   - `RAI_PROFILE`
   - `RAI_DB`
   - `RAI_ENGINE`
1. Execute `run_rai_sequence.py` via
   - Call to Poetry shell
       - `poetry run python3 run_rai_sequence.py`
   - Within Poetry shell
       - `poetry shell`
       - `python3 run_rai_sequence.py`
   - Output is available in the `logs/` directory
