## Development
You can install the required packages using
```bash
uv sync
```

## Tests
Tests can be run in two ways, which you can install with
```bash
uv tool install tox --with tox-uv --upgrade
```

To individually run tests on the current python version, you can use
```bash
uv run poe stubtest
uv run poe mypy
uv run poe basedpyright
```
Though note that if you source the venv, uv run can be omitted from these.


But for backwards compatibility, we have 
```bash
uvx tox p
```
which runs tests for both 3.8 and 3.10 in parallel.
