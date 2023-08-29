## Environment aggregation daemon

`environmentd` aggregates the status of the lower level environment daemons over a specified time interval and determines whether it is safe to observe.

`environment` is a commandline utility that queries the environment daemon.

### Configuration

Configuration is read from json files that are installed by default to `/etc/environmentd`.
A configuration file is specified when launching the server, and the `environment` frontend will search this location when launched.

The configuration options are:
```python
{
  "daemon": "observatory_environment", # Run the server as this daemon. Daemon types are registered in `rockit.common.daemons`.
  "log_name": "environmentd", # The name to use when writing messages to the observatory log.
  "window_length": 1200, # Sliding time window to evaluate conditions over (seconds).
  "control_machines": ["OneMetreDome", "OneMetreTCS"],  # Machine names that are allowed to clear environment history. Machine names are registered in `rockit.common.IP`.
  "watchers": {
    "w1m_vaisala": { # Each watcher specifies a daemon service that should be queried.
      "label": "W1m Vaisala", # Human readable label for this environment sensor.
      "daemon": "onemetre_vaisala", # Daemon to query. Daemon types are registered in `rockit.common.daemons`.
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

The automated packaging scripts will push 5 RPM packages to the observatory package repository:

| Package                         | Description                                                                         |
|---------------------------------|-------------------------------------------------------------------------------------|
| rockit-environment-server       | Contains the `environmentd` server and systemd service file.                        |
| rockit-environment-client       | Contains the `environment` commandline utility for querying the environment server. |
| rockit-environment-data-lapalma | Contains the json configuration for the La Palma telescopes.                        |
| rockit-environment-data-warwick | Contains the json configuration for the Windmill Hill observatory.                  |
| python3-rockit-environment      | Contains the python module with shared code.                                        |

After installing the server package, the systemd service should be enabled:

```
sudo systemctl enable --now environmentd@<config>
sudo systemctl start environmentd
```

where `config` is the name of the json file for the appropriate site.

Now open a port in the firewall:
```
sudo firewall-cmd --zone=public --add-port=<port>/tcp --permanent
sudo firewall-cmd --reload
```
where `port` is the port defined in `rockit.common.daemons` for the daemon specified in the server config.

### Upgrading Installation

New RPM packages are automatically created and pushed to the package repository for each push to the `master` branch.
These can be upgraded locally using the standard system update procedure:
```
sudo yum clean expire-cache
sudo yum update
```

The daemon should then be restarted to use the newly installed code:
```
sudo systemctl restart environmentd@<config>
```

### Testing Locally

The server and client can be run directly from a git clone:
```
./environmentd lapalma.json
ENVIRONMENTD_CONFIG_PATH=./lapalma.json ./environment status
```
