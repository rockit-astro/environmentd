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

"""Class used for aggregating daemon state over time"""

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=broad-except

from collections import deque
import datetime
import math
import threading
import time
from warwick.observatory.common import log

class PyroWatcher:
    """Watches the state of a Pyro daemon implementing the last_measurement convention"""
    def __init__(self, daemon_name, daemon, query_delay, max_data_gap, window_length, parameters):
        self.daemon_name = daemon_name
        self._daemon = daemon
        self._query_delay = query_delay
        self._max_data_gap = max_data_gap
        self._window_length = window_length
        self._parameters = parameters
        self._last_query_failed = False

        # Place a hard limit on the number of stored measurements to simplify
        # cleanup.  Additional filtering is required when iterating the queue.
        queue_len = window_length.seconds * \
            1.1 / query_delay
        self._data = deque(maxlen=math.ceil(queue_len))

        runloop = threading.Thread(target=self.__run_thread)
        runloop.daemon = True
        runloop.start()

    def __run_thread(self):
        """Run loop for monitoring the hardware daemon"""
        while True:
            now = datetime.datetime.utcnow
            try:
                # The delay between queries is greater than the comm timeout
                # so there is no point caching the proxy between loops
                with self._daemon.connect() as daemon:
                    data = daemon.last_measurement()

                if data is not None:
                    # Pryo doesn't deserialize dates, so we manually manage this.
                    data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%SZ')
                    if now() - data['date'] > self._max_data_gap:
                        print('{} WARNING: recieved stale data from {}: {}' \
                        .format(now(), self.daemon_name, data['date']))

                    self._data.append(data)

                    if self._last_query_failed or len(self._data) == 1:
                        prefix = 'Restored' if self._last_query_failed else 'Established'
                        log.info('environmentd', prefix + ' contact with ' + self.daemon_name)
                    self._last_query_failed = False
                else:
                    print('{} WARNING: recieved empty data from {}' \
                        .format(now(), self.daemon_name))
                    if not self._last_query_failed:
                        log.error('environmentd', 'Lost contact with ' + self.daemon_name)
                    self._last_query_failed = True
            except Exception as exception:
                print('{} ERROR: failed to query from {}: {}' \
                      .format(now(), self.daemon_name, str(exception)))
                if not self._last_query_failed:
                    log.error('environmentd', 'Lost contact with ' + self.daemon_name)

                self._last_query_failed = True
            time.sleep(self._query_delay)

    def status(self):
        """Queries the aggregate status of the monitored daemon.
           Returns a dictionary of data"""

        # Filter data for the measurements in our desired time window
        window_start = datetime.datetime.utcnow() - self._window_length
        stale_threshold = datetime.datetime.utcnow() - self._max_data_gap

        measurements = [m for m in self._data if m['date'] >= window_start]
        return {p.name: p.aggregate(measurements, stale_threshold) for p in self._parameters}

    def clear_history(self):
        """Clear the cached measurements"""
        self._data.clear()
