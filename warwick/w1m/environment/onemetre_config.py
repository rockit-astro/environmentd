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
    SunMoonWatcher,
    AggregateParameter,
    FilterInvalidAggregateParameter,
    AggregateBehaviour)

# Delay (in seconds) that we must wait after weather conditions return to
# nominal values before we consider it safe to open the dome.  This also applies
# to the initial startup, while we wait to build sufficient history.
CONDITION_WINDOW_LENGTH = datetime.timedelta(minutes=20)

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
ROOMALERT_QUERY_DELAY = 10
SUPERWASP_QUERY_DELAY = 10
TNG_QUERY_DELAY = 300
POWER_QUERY_DELAY = 10
DISKSPACE_QUERY_DELAY = 30
NETPING_QUERY_DELAY = 30

# Safe operating ranges. Dome will be closed if these parameters aren't met
VAISALA_PARAMETERS = [
    FilterInvalidAggregateParameter('wind_speed', AggregateBehaviour.Range, limits=(0, 40),
                                    warn_limits=(0, 30)),
    FilterInvalidAggregateParameter('median_wind_speed', AggregateBehaviour.Median, limits=(0, 25),
                                    warn_limits=(0, 15), measurement_name='wind_speed'),
    FilterInvalidAggregateParameter('temperature', AggregateBehaviour.Range, limits=(0, 50),
                                    warn_limits=(3, 30)),
    FilterInvalidAggregateParameter('relative_humidity', AggregateBehaviour.Range, limits=(0, 75),
                                    warn_limits=(0, 50)),
    FilterInvalidAggregateParameter('pressure', AggregateBehaviour.Range),
    FilterInvalidAggregateParameter('accumulated_rain', AggregateBehaviour.Range, limits=(0, 0)),
    FilterInvalidAggregateParameter('dew_point_delta', AggregateBehaviour.Range, limits=(2, 100),
                                    warn_limits=(10, 100)),
]

GOTO_VAISALA_PARAMETERS = [
    FilterInvalidAggregateParameter('wind_speed', AggregateBehaviour.Range, limits=(0, 40),
                                    warn_limits=(0, 30)),
    FilterInvalidAggregateParameter('median_wind_speed', AggregateBehaviour.Median, limits=(0, 25),
                                    warn_limits=(0, 15), measurement_name='wind_speed'),
    FilterInvalidAggregateParameter('temperature', AggregateBehaviour.Range, limits=(0, 50),
                                    warn_limits=(3, 30)),
    FilterInvalidAggregateParameter('relative_humidity', AggregateBehaviour.Range, limits=(0, 75),
                                    warn_limits=(0, 50)),
    FilterInvalidAggregateParameter('pressure', AggregateBehaviour.Range),
    FilterInvalidAggregateParameter('accumulated_rain', AggregateBehaviour.Range, limits=(0, 0)),
    FilterInvalidAggregateParameter('dew_point_delta', AggregateBehaviour.Range, limits=(2, 100),
                                    warn_limits=(10, 100)),
]

ROOMALERT_PARAMETERS = [
    AggregateParameter('internal_temp', AggregateBehaviour.Range, limits=(0, 50),
                       warn_limits=(3, 30)),
    AggregateParameter('internal_humidity', AggregateBehaviour.Range, limits=(0, 75),
                       warn_limits=(0, 50)),
    AggregateParameter('roomalert_temp', AggregateBehaviour.Range),
    AggregateParameter('roomalert_humidity', AggregateBehaviour.Range),
    AggregateParameter('truss_temp', AggregateBehaviour.Range),
    AggregateParameter('hatch_closed', AggregateBehaviour.Set),
    AggregateParameter('trap_closed', AggregateBehaviour.Set),
    AggregateParameter('security_system_safe', AggregateBehaviour.Latest, limits=(1, 1)),
]

SUPERWASP_PARAMETERS = [
    AggregateParameter('wind_speed', AggregateBehaviour.Range, limits=(0, 40), warn_limits=(0, 30)),
    AggregateParameter('median_wind_speed', AggregateBehaviour.Median, limits=(0, 25),
                       warn_limits=(0, 15), measurement_name='wind_speed'),
    AggregateParameter('sky_temp', AggregateBehaviour.Range),
    AggregateParameter('ext_temperature', AggregateBehaviour.Range, limits=(0, 50),
                       warn_limits=(3, 30)),
    AggregateParameter('ext_humidity', AggregateBehaviour.Range, limits=(0, 75),
                       warn_limits=(0, 50)),
    AggregateParameter('dew_point_delta', AggregateBehaviour.Range, limits=(2, 100),
                       warn_limits=(10, 100)),
]

TNG_PARAMETERS = [
    FilterInvalidAggregateParameter('dust', AggregateBehaviour.Latest),
    FilterInvalidAggregateParameter('solarimeter', AggregateBehaviour.Latest),
    FilterInvalidAggregateParameter('seeing', AggregateBehaviour.Latest),
]

DISKSPACE_PARAMETERS = [
    AggregateParameter('data_fs_available_bytes', AggregateBehaviour.Latest,
                       limits=(5 * 2**30, 2**40), warn_limits=(10 * 2**30, 2**40)),
    AggregateParameter('data_fs_percent_available', AggregateBehaviour.Latest, limits=(5, 100),
                       warn_limits=(10, 100)),
]

NETPING_PARAMETERS = [
    AggregateParameter('google', AggregateBehaviour.Range, ignore_values=[-1], limits=(0, 2000)),
    AggregateParameter('ngtshead', AggregateBehaviour.Range, ignore_values=[-1], limits=(0, 2000)),
]

POWER_PARAMETERS = [
    AggregateParameter('main_ups_status', AggregateBehaviour.Set, valid_set_values=set([2])),
    AggregateParameter('main_ups_battery_healthy', AggregateBehaviour.Set),
    AggregateParameter('main_ups_battery_remaining', AggregateBehaviour.Range, limits=(85, 101),
                       warn_limits=(99, 101)),
    AggregateParameter('dome_ups_status', AggregateBehaviour.Set, valid_set_values=set([2])),
    AggregateParameter('dome_ups_battery_healthy', AggregateBehaviour.Set),
    AggregateParameter('dome_ups_battery_remaining', AggregateBehaviour.Range, limits=(85, 101),
                       warn_limits=(99, 101)),
    AggregateParameter('light', AggregateBehaviour.Set),
]

class OneMetreConfig:
    """Configuration for the W1m's Enviroment daemon"""
    control_ips = [IP.OneMetreDome, IP.OneMetreTCS]
    watchers = [
        PyroWatcher('vaisala', daemons.onemetre_vaisala, VAISALA_QUERY_DELAY,
                    TIME_GAP_MAX, CONDITION_WINDOW_LENGTH, VAISALA_PARAMETERS),
        PyroWatcher('goto_vaisala', daemons.goto_vaisala, VAISALA_QUERY_DELAY,
                    TIME_GAP_MAX, CONDITION_WINDOW_LENGTH, GOTO_VAISALA_PARAMETERS),
        PyroWatcher('roomalert', daemons.onemetre_roomalert, ROOMALERT_QUERY_DELAY,
                    TIME_GAP_MAX, CONDITION_WINDOW_LENGTH, ROOMALERT_PARAMETERS),
        PyroWatcher('superwasp', daemons.superwasp_log, SUPERWASP_QUERY_DELAY,
                    SUPERWASP_TIME_GAP_MAX, CONDITION_WINDOW_LENGTH, SUPERWASP_PARAMETERS),
        PyroWatcher('tng', daemons.tng_log, TNG_QUERY_DELAY, TNG_TIME_GAP_MAX,
                    CONDITION_WINDOW_LENGTH, TNG_PARAMETERS),
        PyroWatcher('diskspace', daemons.onemetre_tcs_diskspace,
                    DISKSPACE_QUERY_DELAY, DISKSPACE_TIME_GAP_MAX,
                    CONDITION_WINDOW_LENGTH, DISKSPACE_PARAMETERS),
        PyroWatcher('netping', daemons.observatory_network_ping,
                    NETPING_QUERY_DELAY, NETPING_TIME_GAP_MAX, CONDITION_WINDOW_LENGTH,
                    NETPING_PARAMETERS),
        PyroWatcher('power', daemons.onemetre_power, POWER_QUERY_DELAY,
                    TIME_GAP_MAX, CONDITION_WINDOW_LENGTH, POWER_PARAMETERS),
        SunMoonWatcher('ephem')
    ]
