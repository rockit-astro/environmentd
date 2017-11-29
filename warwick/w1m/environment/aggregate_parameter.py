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

"""Class used for aggregating environment sensor status over a time range"""

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments

import statistics
from .constants import ParameterStatus

class AggregateBehaviour:
    """Aggregation behaviour"""
    RangeWithLimits, Range, MedianWithLimits, Median, LatestWithLimits, Latest, Set = range(7)

class AggregateParameter:
    """Defines the aggregation behaviour for a specific environment parameter"""
    def __init__(self, name, behaviour, limits=None, valid_set_values=None, measurement_name=None):
        self.name = name
        self._behaviour = behaviour
        self._limits = limits
        self._valid_set_values = valid_set_values
        self.has_limits = self.__has_limits()

        self._measurement_name = measurement_name if measurement_name is not None else name

    def __has_limits(self):
        """Returns true if this parameter has limits"""
        if self._behaviour == AggregateBehaviour.Set:
            return self._valid_set_values is not None

        return self._behaviour in [
            AggregateBehaviour.RangeWithLimits,
            AggregateBehaviour.MedianWithLimits,
            AggregateBehaviour.LatestWithLimits
        ]

    def aggregate(self, measurements):
        """Status data for the web dashboard"""
        ret = {
            'status': ParameterStatus.Unsafe,
        }

        if self.has_limits:
            ret['limits'] = self._limits

        if not measurements:
            ret['error'] = 'NO DATA'
            return ret

        if self._behaviour == AggregateBehaviour.RangeWithLimits or \
                self._behaviour == AggregateBehaviour.Range:

            ret['min'] = measurements[0][self._measurement_name]
            ret['max'] = ret['min']
            for measurement in measurements:
                value = measurement[self._measurement_name]
                ret['min'] = min(value, ret['min'])
                ret['max'] = max(value, ret['max'])
                ret['latest'] = value

            if ret['min'] >= self._limits[0] and ret['max'] <= self._limits[1]:
                ret['status'] = ParameterStatus.Safe

        elif self._behaviour == AggregateBehaviour.MedianWithLimits or \
                self._behaviour == AggregateBehaviour.Median:

            ret['latest'] = statistics.median([m[self._measurement_name] for m in measurements])
            if ret['latest'] >= self._limits[0] \
                    and ret['latest'] <= self._limits[1]:
                ret['status'] = ParameterStatus.Safe

        elif self._behaviour == AggregateBehaviour.Set:
            ret['latest'] = measurements[-1][self._measurement_name]

            # Convert to a set to remove duplicates
            values = set([m[self._measurement_name] for m in measurements])

            # Convert back to a list so it can be serialized as json
            ret['values'] = list(values)

            # If all values are valid the set difference against _valid_set_values will be empty
            if not values - self._valid_set_values:
                ret['status'] = ParameterStatus.Safe

            if self._valid_set_values:
                ret['valid_values'] = list(self._valid_set_values)

        else:
            latest = measurements[-1][self._measurement_name]
            ret['latest'] = latest

            if latest >= self._limits[0] and latest <= self._limits[1]:
                ret['status'] = ParameterStatus.Safe

        return ret
