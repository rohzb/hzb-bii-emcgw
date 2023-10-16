# EMC TCP Gateway

The EMC TCP Gateway allows users to control a monochromator from a different network segment using the EMC protocol over TCP. This is intended for use when the user's computer is in a fully isolated network segment and the monochromator is in another network segment.

The EMC TCP Gateway is designed to run on a border computer at the edge of the isolated network segment. It listens for incoming TCP connections from user computers and forwards those connections to the monochromator over TCP. The gateway can also filter clients by IP address, which can be useful for security reasons.

## a few words about EMC protocol

The EMC protocol is an extension of the AMC protocol, which is used to control monochromators. The EMC protocol adds new commands and features that are necessary for the continuous mode, where the monochromator moves continuously from a start- to an end-energy. The EMC protocol also allows the client to set and read various monochromator parameters and retrieve error messages after a failed request. Finally, the EMC protocol includes a fast energy readback command that allows the readout of the current photon energy with significantly increased speed.

# Usage

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

