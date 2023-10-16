# EMC TCP Gateway

The EMC TCP Gateway allows users to control a monochromator from a different network segment using the EMC protocol over TCP. This is intended for use when the user's computer is in a fully isolated network segment and the monochromator is in another network segment.

The EMC TCP Gateway is designed to run on a border computer at the edge of the isolated network segment. It listens for incoming TCP connections from user computers and forwards those connections to the monochromator over TCP. The gateway can also filter clients by IP address, which can be useful for security reasons.

## a few words about EMC protocol

The EMC protocol is an extension of the AMC protocol, which is used to control monochromators. The EMC protocol adds new commands and features that are necessary for the continuous mode, where the monochromator moves continuously from a start- to an end-energy. The EMC protocol also allows the client to set and read various monochromator parameters and retrieve error messages after a failed request. Finally, the EMC protocol includes a fast energy readback command that allows the readout of the current photon energy with significantly increased speed.

# Usage

1. **Basic Usage:**

   To start the server with default settings, you can simply run the following command:

   ```bash
   emcgw
   ```

2. **Specify Listen and Connect Hosts:**

   You can specify the listen host and connect host using command-line options. For example:

   ```bash
   emcgw -l 0.0.0.0 -p 8080 -r example.com -P 80
   ```

3. **Verbosity Levels:**

   Increase verbosity level for debugging using the `-v` option. For example:

   ```bash
   emcgw -v             # Increase verbosity level (INFO)
   emcgw -vv            # Increase verbosity level (DEBUG)
   emcgw -vvv           # Increase verbosity level (TRACE)
   ```

4. **Specify Configuration File:**

   You can also specify a YAML configuration file with all the settings:

   ```bash
   emcgw -c config.yaml
   ```

   Here is an example `config.yaml` file:

   ```yaml
   listen_host: 0.0.0.0
   listen_port: 8080
   connect_host: example.com
   connect_port: 80
   log_level: DEBUG
   allowed_clients:
     - 192.168.1.1
     - "10.0.0.0/8"
     - example.net
   ```

5. **Multiple Configuration Files:**

   You can provide multiple configuration files, and they will be read one after another:

   ```bash
   emcgw -c config1.yaml -c config2.yaml
   ```

6. **Custom Log Levels:**

   You can use custom log levels when specifying the log level:

   ```bash
   emcgw -L VERBOSE      # Custom log level for more detailed information
   emcgw -L TRACE        # Custom log level for maximum verbosity
   ```

Remember to customize these examples based on the actual options and features of your application.


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

