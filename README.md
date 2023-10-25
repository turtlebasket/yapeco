# `yapeco`: Yet Another Python Envvar Config Object

A positively miniscule utility module to access `.env` (and otherwise environment-defined) config values through a Python object. Created out of annoyance with not being able to autocomplete said envvars in my editor :^)

## Usage

Installation:

```bash
pip3 install yapeco
```

A simple example:

```bash
# -- [mock environment] ---------------------------
API_KEY=abc123
DELAY_MSEC=18
FEATURE_A_ENABLED=false
FEATURE_B_ENABLED=1
```

```python
# --- config.py -----------------------------------

from yapeco import BaseEnvironment as Env

class Config(Env):
    api_key: str
    delay_msec: int
    feature_a_enabled: bool
    feature_b_enabled: bool


# --- main.py -------------------------------------

from config import Config

Config.api_key # "abc123"
Config.delay_msec # 18
Config.feature_a_enabled # False
Config.feature_b_enabled # True
```

## Features & Limitations

- Case-insensitive + `SNAKE_case` field names
- Primitives such as `str`, `bool`, `int` and `float` are supported (no guarantees with the latter, though)
- Common boolean config formats (i.e. `VAR=0/1/true/false/True/False`) work as expected
- Errors at start time if an environment variable is not found
- Does not support types from `typing`, e.g. `Optional[str]`

## Development

Requires [poetry](https://python-poetry.org/).

```bash
poetry install # install dependencies
poetry build # build package
poetry run pytest # run tests
```

## Extra

Pedantic note:

> As in Smalltalk, classes themselves are objects. 
>
> —[The Literal Python Documentation](https://docs.python.org/3/tutorial/classes.html)
