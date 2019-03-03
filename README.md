## Environment aggregation daemon [![Travis CI build status](https://travis-ci.org/warwick-one-metre/environmentd.svg?branch=master)](https://travis-ci.org/warwick-one-metre/environmentd)

Part of the observatory software for the Warwick one-meter and RASA prototype telescopes.

`environmentd` aggregates the status of the lower level enviroment daemons over a specified time interval and determines whether it is safe to observe.

`environment` is a commandline utility that queries the environment daemon.

`python36-warwick-observatory-environment` is a python module with the common environment code.

### Software Setup

After installation, the `observatory-environment-server` must be enabled using:
```
sudo systemctl enable enivironmentd.service
```

The service will automatically start on system boot, or you can start it immediately using:
```
sudo systemctl start enivironmentd.service
```

Finally, open a port in the firewall so that other machines on the network can access the daemon:
```
sudo firewall-cmd --zone=public --add-port=9028/tcp --permanent
sudo firewall-cmd --reload
```

Weather stations and other daemons that should be monitored are defined in `sensors.json`. 
It should not be necessary to modify the python code unless you want to define new display formats for the `environment` command line tool.