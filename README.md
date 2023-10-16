# EMC TCP Gateway

The EMC TCP Gateway allows users to control a monochromator from a different network segment using the EMC protocol over TCP. This is intended for use when the user's computer is in a fully isolated network segment and the monochromator is in another network segment.

The EMC TCP Gateway is designed to run on a border computer at the edge of the isolated network segment. It listens for incoming TCP connections from user computers and forwards those connections to the monochromator over TCP. The gateway can also filter clients by IP address, which can be useful for security reasons.

## About EMC protocol

The EMC protocol is an extension of the AMC protocol, which is used to control monochromators. The EMC protocol adds new commands and features that are necessary for the continuous mode, where the monochromator moves continuously from a start- to an end-energy. The EMC protocol also allows the client to set and read various monochromator parameters and retrieve error messages after a failed request. Finally, the EMC protocol includes a fast energy readback command that allows the readout of the current photon energy with significantly increased speed.

# How to use

To use the EMC TCP Gateway, you can either run the server with default settings or customize the server settings and specify allowed clients via command-line arguments. You can also configure the server using a YAML file.

Here are some examples:

### Example 1: Running the Server with Default Settings
To start the server with default settings, you can simply run the `emcgw` command:

```bash
emcgw
```

In this mode, the server will listen on the default host "localhost," port 8080, and connect to the target host "example.com" on port 80. The log level will be set to "INFO."

### Example 2: Custom Server Configuration
You can customize the server settings and specify allowed clients via command-line arguments. Here's an example:

```bash
emcgw -l localhost -p 8080 -r example.com -P 80 -L DEBUG -v -a 192.168.1.0/24 192.168.2.0/24
```

In this example:
- `-l localhost` sets the host for the server to listen on to "localhost."
- `-p 8080` sets the port to bind to as 8080.
- `-r example.com` specifies the target host to connect to as "example.com."
- `-P 80` sets the target port to connect to as 80.
- `-L DEBUG` sets the log level to "DEBUG," providing more detailed logging.
- `-v` increases the verbosity level, resulting in even more detailed logging (use multiple `-v` flags for higher verbosity).
- `-a 192.168.1.0/24 192.168.2.0/24` specifies a list of allowed clients using IP/CIDR notation.

### Example 3: Configuration via YAML File
You can also configure the server using a YAML file. Create a configuration file, e.g., `config.yaml`, with the following contents:

```yaml
listen_host: "localhost"
listen_port: 8080
connect_host: "example.com"
connect_port: 80
log_level: "INFO"
allowed_clients:
  - "192.168.1.0/24"
  - "192.168.2.0/24"
```

Then, you can start the server by providing the path to the configuration file:

```bash
emcgw -c config.yaml
```

The server will read the configuration settings from the YAML file, including the host to listen on, the port to bind to, the target host to connect to, the log level, and the list of allowed clients.

**Note:** You can also specify the access order in the YAML file if needed. If not specified, the default is "allow-first."

These examples demonstrate how to run and configure the `emcgw` server, either via command-line arguments or a YAML configuration file.


# Installation

**Note:** The instlation section is for the current "under development" version. ^

Clone this repository and run `scripts/bootstrap.sh` to initialize the python virtual environment and set up needed dependencies.

Running tests with coverage:
```bash
> pytest --cov=PROJECT-NAME-HERE tests/
```

# Repository structure

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

