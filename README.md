# Title of the project

Info about the project

## Usage

Please see examples of the current API features in the [examples](examples/) directory.

There is some documentation included as a doc strings to the classes, but for now it is not yet comprehensive as the API is a subject to change. 


## Installation

Clone this repository and run `scripts/bootstrap.sh` to initialize the python virtual environment and set up needed dependencies.

Running tests with coverage:
```bash
> pytest --cov=PROJECT-NAME-HERE tests/
```

## Repository structure

| path                             | description       |
| ----------------------------     | ----------------- |
| [CHANGELOG.md](CHANGELOG.md)     | version changelog |
| [examples](examples/)            | Examples using the package |
| [LICENSE](LICENSE)               | License information |
| [pyproject.toml](pyproject.toml) | python package installation rules |
| README.md                        | this readme file     |
| [scripts](scripts/)              | helper scripts |
| [src](src/)                      | source code of the package |
| [requirements.txt](requirements.txt) | packages needed to run the examples but not dependencies of this package|
| [dev-requirements.txt](dev-requirements.txt) | packages needed for the package development, e.g. `pytest`|
| [tests](tests/)                      | `pytest` tests |

