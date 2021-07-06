## Environment aggregation daemon

`environmentd` aggregates the status of the lower level environment daemons over a specified time interval and determines whether it is safe to observe.

`environment` is a commandline utility that queries the environment daemon.

`python3-warwick-observatory-environment` is a python module with the common environment code.

See [Software Infrastructure](https://github.com/warwick-one-metre/docs/wiki/Software-Infrastructure) for an overview of the observatory software architecture and instructions for developing and deploying the code.

### Configuration

Configuration for the shared site daemon is read from `/etc/environmentd/sensors.json` that is specified when launching the server.

The configuration options are:
```python
{
  "daemon": "observatory_environment", # Run the server as this daemon. Daemon types are registered in `warwick.observatory.common.daemons`.
  "log_name": "environmentd", # The name to use when writing messages to the observatory log.
  "window_length": 1200, # Sliding time window to evaluate conditions over (seconds).
  "control_machines": ["OneMetreDome", "OneMetreTCS", "RASAMain"],  # Machine names that are allowed to clear environment history. Machine names are registered in `warwick.observatory.common.IP`.
  "watchers": {
    "w1m_vaisala": { # Each watcher specifies a daemon service that should be queried.
      "label": "W1m Vaisala", # Human readable label for this environment sensor.
      "daemon": "onemetre_vaisala", # Daemon to query. Daemon types are registered in `warwick.observatory.common.daemons`.
      "query_rate": 10, # Rate to query environment state (seconds).
      "stale_age": 30, # Environment state older than this is considered to be invalid (seconds).
      "parameters": { # Each parameter corresponds to an entry in the dictionary returned by the `last_measurement` method.
        "wind_speed": { # Key name in the daemon measurement data.
          "label": "Wind", # Human readable label for this parameter.
          "unit": "km/h", # Human readable unit label for this parameter.
          "type": "Range", # Type of processing to determine the current value and whether it is safe. Accepts values in ['Range', 'Median', 'Latest', 'Set'].
          "filter_invalid": true, # Ignore measurement if `wind_speed_valid` in the measurement data is false.
          "warn_limits": [0, 30], # Measurements outside this range should be formatted as a warning but are not necessarily unsafe.
          "unsafe_limits": [0, 40] # Measurements outside this range are considered unsafe.
        }
        # Additional parameters can be defined
      }
      # Additional watchers can be defined
    }
  }
}
```
### Initial Installation

The automated packaging scripts will push 3 RPM packages to the observatory package repository:

| Package           | Description |
| ----------------- | ------ |
| observatory-environment-server | Contains the `environmentd` server and systemd service file. |
| observatory-environment-client | Contains the `environment` commandline utility for quering the environment server. |
| python3-warwick-observatory-environment | Contains the python module with shared code. |

The `observatory-environment-server` and `observatory-environment-client` packages should be installed on the `gotoserver` machine.
The `observatory-environment-client` package can be installed on any other machine where you would like to query status.

After installing the server package, the systemd service should be enabled:

```
sudo systemctl enable environmentd
sudo systemctl start environmentd
```

Now open a port in the firewall:
```
sudo firewall-cmd --zone=public --add-port=<port>/tcp --permanent
sudo firewall-cmd --reload
```
where `port` is the port defined in `warwick.observatory.common.daemons` for the daemon specified in the server config.

### Upgrading Installation

New RPM packages are automatically created and pushed to the package repository for each push to the `master` branch.
These can be upgraded locally using the standard system update procedure:
```
sudo yum clean expire-cache
sudo yum update
```

The daemon should then be restarted to use the newly installed code:
```
sudo systemctl stop environmentd
sudo systemctl start environmentd
```

### Testing Locally

The server and client can be run directly from a git clone:
```
./environmentd sensors.json
./environment status
```

`environment` currently hardcodes queries to the `observatory_environment` daemon. You may need to manually replace this with e.g. `localhost_test` when testing locally.