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

### Example 4: Using Allowed and Denied Clients with "Deny-First" Access Order and Two Config Files

First, create two configuration files, e.g., `config_base.yaml` and `config_custom.yaml` with the following contents:

**config_base.yaml**:
```yaml
listen_host: "localhost"
listen_port: 8080
connect_host: "example.com"
connect_port: 80
log_level: "INFO"
```

**config_custom.yaml**:
```yaml
allowed_clients:
  - "192.168.1.0/24"
denied_clients:
  - "192.168.1.10"
  - "192.168.2.0/24"
access_order: "deny-first"
```

Now, you can start the server using these configuration files:

```bash
emcgw -c config_base.yaml config_custom.yaml
```

Here's what this updated example does:
- `-c config_base.yaml config_custom.yaml` specifies two configuration files to use. The settings in `config_base.yaml` serve as the base configuration, and settings in `config_custom.yaml` will override any matching settings from the base configuration.

In this setup, it will use the base configuration from `config_base.yaml` for general settings and override access control settings with the specified allowed and denied clients and access order from `config_custom.yaml`. The server will use "deny-first" access order, and clients in the denied list will be denied access.

This allows you to have a common base configuration and easily customize access control by specifying only the necessary changes in a separate configuration file.

Note: Please make sure that these configuration files exist and are correctly formatted in YAML. The `-c` flag allows you to specify one or more configuration files to merge and apply their settings to the server.

Example 5: Using Allowed and Denied Clients with "Allow-First" Access Order
In this example, we configure the server to use "allow-first" access order, which means clients in the allowed list take precedence over the denied list. We also specify both allowed and denied clients.

bash
Copy code
emcgw -l localhost -p 8080 -r example.com -P 80 -L DEBUG -v -a 192.168.1.0/24 -d 192.168.1.10 -d 192.168.2.0/24 --access-order allow-first
Here's what this example does:

-l localhost sets the host for the server to listen on to "localhost."
-p 8080 sets the port to bind to as 8080.
-r example.com specifies the target host to connect to as "example.com."
-P 80 sets the target port to connect to as 80.
-L DEBUG sets the log level to "DEBUG," providing more detailed logging.
-v increases the verbosity level for even more detailed logging.
-a 192.168.1.0/24 specifies a list of allowed clients using IP/CIDR notation.
-d 192.168.1.10 -d 192.168.2.0/24 specifies two clients in the denied list.
--access-order allow-first sets the access order to "allow-first."
In this setup, clients in the allowed list (192.168.1.0/24) will be allowed access, even if they are also in the denied list. Clients in the denied list (192.168.1.10 and the entire 192.168.2.0/24 network) will be denied access.

Note: These examples demonstrate how to set up access control for your server using both allowed and denied clients. The choice of "allow-first" or "deny-first" determines the access order priority, affecting which clients are granted or denied access.

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

