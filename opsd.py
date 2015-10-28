#!/usr/bin/env python3
#
# This file is part of opsd.
#
# opsd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# opsd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with opsd.  If not, see <http://www.gnu.org/licenses/>.

"""Daemon process for monitoring the low-level hardware daemons.  Hardware
   status and weather conditions are aggregated over a time period, and can
   be queried to determine whether it is safe to observe."""

from collections import deque
import datetime
import math
import Pyro4
import threading
import time

# Settings for this daemon
PYRO_HOST = 'localhost'
PYRO_PORT = 9002
PYRO_COMM_TIMEOUT = 5
VAISALA_DAEMON_URI = 'PYRO:vaisala_daemon@localhost:9001'

# TODO: Include RoomAlert and Power daemons

# Delay (in seconds) that we must wait after weather conditions return to
# nominal values before we consider it safe to open the dome.  This also applies
# to the initial startup, while we wait to build sufficient history.
CONDITION_TIMEOUT_DELAY = datetime.timedelta(minutes=20)

# Safe operating ranges. Dome will be closed if these parameters aren't met
VAISALA_WIND_LIMITS = (0, 30)
VAISALA_TEMPERATURE_LIMITS = (0, 50)
VAISALA_HUMIDITY_LIMITS = (0, 75)
VAISALA_PRESSURE_LIMITS = (600, 1100)

# Maximum gap that we will accept between measurements (due to query failures,
# etc). If this is exceeded, then we will force the dome to close until the
# condition timeout passes.
VAISALA_TIME_GAP_MAX = datetime.timedelta(seconds=30)

# Delay (in seconds) between queries to the vaisala daemon.
# Actual query period will be slightly longer than this due to comms delays.
VAISALA_QUERY_DELAY = 10

class AggregateMeasurement:
    """A collection of measurements of a specific type over time."""
    def __init__(self, limits):
        self._min = 99999999
        self._max = -99999999
        self._count = 0
        self._limit_min = limits[0]
        self._limit_max = limits[1]

    def add(self, measurement):
        """Add a measurement to the aggregate"""
        self._min = min(measurement, self._min)
        self._max = max(measurement, self._max)
        self._count = self._count + 1

    def results(self):
        """Returns a tuple of max value, min value, min date, max date, and
           whether all the measurements fall within the specified limits."""
        if self._count == 0:
            return (0, 0, False)

        valid = self._min > self._limit_min and self._max < self._limit_max
        return (self._min, self._max, valid)

class OperationsDaemon:
    """Daemon class for communicating with the lower level hardware daemons"""

    def __init__(self):
        self._lock = threading.Lock()
        self._running = True

        # Place a hard limit on the number of stored measurements to simplify
        # cleanup.  Additional filtering is required when iterating the queue.
        vaisala_queue_len = CONDITION_TIMEOUT_DELAY.seconds * \
            1.1 / VAISALA_QUERY_DELAY
        self._vaisala_data = deque(maxlen=math.ceil(vaisala_queue_len))

        vaisala_runloop = threading.Thread(target=self.run_vaisala_thread)
        vaisala_runloop.daemon = True
        vaisala_runloop.start()

    def run_vaisala_thread(self):
        """Run loop for monitoring the vaisalad daemon"""
        vaisala = None
        while self._running:
            now = datetime.datetime.utcnow()

            # Query the latest measurement
            # pylint: disable=broad-except
            try:
                if vaisala is None:
                    print('opening new connection')
                    vaisala = Pyro4.Proxy(VAISALA_DAEMON_URI)
                data = vaisala.last_measurement()

                # Deserialize date on the fly
                data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%SZ')
                print(data['date'])

                if now - data['date'] > VAISALA_TIME_GAP_MAX:
                    print('{} WARNING: recieved stale data from vaisalad: {}' \
                      .format(now, date))
                self._vaisala_data.append(data)
            except Exception as exception:
                print('{} ERROR: failed to query from vaisalad: {}' \
                      .format(now, str(exception)))
            # pylint: enable=broad-except

            time.sleep(VAISALA_QUERY_DELAY)

    def status(self):
        """Returns the aggregated status of the monitored daemons.
           Each measurement is a tuple of min value, max value, measurement valid
        """

        # The youngest date that the first measurement can take while remaining valid
        max_first_date = datetime.datetime.utcnow() - CONDITION_TIMEOUT_DELAY

        # The oldest date that the last measurement can take while remaining valid
        min_last_date = datetime.datetime.utcnow() - VAISALA_TIME_GAP_MAX

        wind = AggregateMeasurement(VAISALA_WIND_LIMITS)
        vaisala_temp = AggregateMeasurement(VAISALA_TEMPERATURE_LIMITS)
        vaisala_humidity = AggregateMeasurement(VAISALA_HUMIDITY_LIMITS)
        pressure = AggregateMeasurement(VAISALA_PRESSURE_LIMITS)

        vaisala_date_start = None
        vaisala_date_end = None
        vaisala_sufficient_data = True

        # deque is threadsafe, so we don't need an explicit lock
        for measurement in self._vaisala_data:
            print('{}'.format(measurement))
            date = measurement['date']

            # This is the first measurement with a valid date
            if vaisala_date_start is None:
                vaisala_date_start = date

            if vaisala_date_end is None:
                vaisala_date_end = date

            # Only include measurements within the desired window
            if date > max_first_date:
                if date - vaisala_date_end > VAISALA_TIME_GAP_MAX:
                    print('Gap between {} and {} is too large!'.format(date, vaisala_date_end))
                    vaisala_sufficient_data = False

                wind.add(measurement['wind_speed'])
                vaisala_temp.add(measurement['temperature'])
                vaisala_humidity.add(measurement['relative_humidity'])
                pressure.add(measurement['pressure'])

            vaisala_date_end = date

        # Check that the first measurement was sufficiently old
        if vaisala_date_start is None or vaisala_date_start > max_first_date:
            vaisala_sufficient_data = False

        # Check the time between the last measurement and now
        if vaisala_date_end is None or vaisala_date_end < min_last_date:
            vaisala_sufficient_data = False

        return {
            'vaisala_date_start': vaisala_date_start,
            'vaisala_date_end': vaisala_date_end,
            'vaisala_sufficient_data': vaisala_sufficient_data,
            'wind': wind.results(),
            'pressure': pressure.results(),
            'vaisala_temp': vaisala_temp.results(),
            'vaisala_humidity': vaisala_humidity.results(),
        }

    def running(self):
        """Returns false if the daemon should be terminated"""
        return self._running

    def stop(self):
        """Stop the daemon thread"""
        self._running = False

def spawn_daemon():
    """Spawns the daemon and registers it with Pyro"""
    Pyro4.config.COMMTIMEOUT = PYRO_COMM_TIMEOUT
    pyro = Pyro4.Daemon(host=PYRO_HOST, port=PYRO_PORT)

    ops = OperationsDaemon()
    uri = pyro.register(ops, objectId='ops_daemon')

    print('Starting ops daemon with Pyro ID:', uri)
    pyro.requestLoop(loopCondition=ops.running)
    print('Stopping ops daemon with Pyro ID:', uri)

if __name__ == '__main__':
    spawn_daemon()
