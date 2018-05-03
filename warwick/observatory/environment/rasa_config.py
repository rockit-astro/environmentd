#!/usr/bin/env python3
#
# This file is part of environmentd
#
# environmentd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# environmentd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with environmentd.  If not, see <http://www.gnu.org/licenses/>.

"""Configuration for the W1m's Enviroment daemon"""

# pylint: disable=too-few-public-methods
import datetime
from warwick.observatory.common import daemons, IP
from . import (
    PyroWatcher,
    SunMoonWatcher)
from .parameters import (
    vaisala_parameters,
    superwasp_parameters,
    tng_parameters,
    diskspace_parameters,
    netping_parameters)

# Delay (in seconds) that we must wait after weather conditions return to
# nominal values before we consider it safe to open the dome.  This also applies
# to the initial startup, while we wait to build sufficient history.
WINDOW_LENGTH = datetime.timedelta(minutes=20)

# Maximum gap that we will accept between measurements (due to query failures,
# etc). If this is exceeded, then we will force the dome to close until the
# condition timeout passes.
TIME_GAP_MAX = datetime.timedelta(seconds=30)
TNG_TIME_GAP_MAX = datetime.timedelta(minutes=10)
DISKSPACE_TIME_GAP_MAX = datetime.timedelta(minutes=1)
NETPING_TIME_GAP_MAX = datetime.timedelta(minutes=5)
SUPERWASP_TIME_GAP_MAX = datetime.timedelta(seconds=60)

# Delay (in seconds) between update iterations.
# Actual query period will be slightly longer than this due to comms delays.
VAISALA_QUERY_DELAY = 10
SUPERWASP_QUERY_DELAY = 10
TNG_QUERY_DELAY = 300
DISKSPACE_QUERY_DELAY = 30
NETPING_QUERY_DELAY = 30

VAISALA_LIMITS = {
    'wind_speed': (0, 40),
    'median_wind_speed': (0, 25),
    'temperature': (0, 50),
    'relative_humidity': (0, 75),
    'accumulated_rain': (0, 0),
    'dew_point_delta': (2, 100)
}
VAISALA_WARN_LIMITS = {
    'wind_speed': (0, 30),
    'median_wind_speed': (0, 15),
    'temperature': (3, 30),
    'relative_humidity': (0, 50),
    'dew_point_delta': (10, 100)
}

SUPERWASP_LIMITS = {
    'wind_speed': (0, 40),
    'median_wind_speed': (0, 25),
    'ext_temperature': (0, 50),
    'ext_humidity': (0, 75),
    'dew_point_delta': (2, 100)
}
SUPERWASP_WARN_LIMITS = {
    'wind_speed': (0, 30),
    'median_wind_speed': (0, 15),
    'ext_temperature': (3, 30),
    'ext_humidity': (0, 50),
    'dew_point_delta': (10, 100)
}

DISKSPACE_LIMITS = {
    'data_fs_available_bytes': (5 * 2**30, 2**40),
    'data_fs_percent_available': (5, 100)
}
DISKSPACE_WARN_LIMITS = {
    'data_fs_available_bytes': (10 * 2**30, 2**40),
    'data_fs_percent_available': (10, 100)
}

NETPING_LIMITS = {
    'google': (0, 2000),
    'ngtshead': (0, 2000),
}

class RASAConfig:
    """Configuration for the RASA prototype's Enviroment daemon"""
    daemon = daemons.rasa_environment
    control_ips = [IP.RASAMain]

    def get_watchers():
        """Returns a list of PyroWatchers to be monitored"""
        return [
            PyroWatcher('vaisala', daemons.onemetre_vaisala, VAISALA_QUERY_DELAY, TIME_GAP_MAX,
                        WINDOW_LENGTH, vaisala_parameters(VAISALA_LIMITS, VAISALA_WARN_LIMITS)),

            PyroWatcher('goto_vaisala', daemons.goto_vaisala, VAISALA_QUERY_DELAY, TIME_GAP_MAX,
                        WINDOW_LENGTH, vaisala_parameters(VAISALA_LIMITS, VAISALA_WARN_LIMITS)),

            PyroWatcher('superwasp', daemons.superwasp_log, SUPERWASP_QUERY_DELAY,
                        SUPERWASP_TIME_GAP_MAX, WINDOW_LENGTH,
                        superwasp_parameters(SUPERWASP_LIMITS, SUPERWASP_WARN_LIMITS)),

            PyroWatcher('tng', daemons.tng_log, TNG_QUERY_DELAY, TNG_TIME_GAP_MAX,
                        WINDOW_LENGTH, tng_parameters()),

            PyroWatcher('diskspace', daemons.rasa_diskspace, DISKSPACE_QUERY_DELAY,
                        DISKSPACE_TIME_GAP_MAX, WINDOW_LENGTH,
                        diskspace_parameters(DISKSPACE_LIMITS, DISKSPACE_WARN_LIMITS)),

            PyroWatcher('netping', daemons.observatory_network_ping, NETPING_QUERY_DELAY,
                        NETPING_TIME_GAP_MAX, WINDOW_LENGTH, netping_parameters(NETPING_LIMITS)),

            SunMoonWatcher('ephem')
        ]
