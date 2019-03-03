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
# pylint: disable=too-many-branches
# pylint: disable=too-many-instance-attributes

import datetime
import statistics


class AggregateBehaviour:
    """Aggregation behaviour"""
    Range, Median, Latest, Set = range(4)

    @classmethod
    def parse(cls, value):
        """Parses a string into an AggregateBehaviour"""
        if value == 'Range':
            return cls.Range
        if value == 'Median':
            return cls.Median
        if value == 'Latest':
            return cls.Latest
        if value == 'Set':
            return cls.Set
        raise ValueError('could not convert string to AggregateBehaviour: ' + value)


class AggregateParameter:
    """Defines the aggregation behaviour for a specific environment parameter"""
    def __init__(self, name, behaviour, label, unit=None, limits=None, warn_limits=None,
                 valid_set_values=None, display=None, measurement_name=None, ignore_values=None):
        self.name = name
        self._label = label
        self._unit = unit
        self._behaviour = behaviour
        self._limits = limits
        self._warn_limits = warn_limits
        self._display = display
        self._valid_set_values = valid_set_values
        self._ignore_values = ignore_values
        self._measurement_name = measurement_name if measurement_name is not None else name

    def aggregate(self, measurements, stale_measurement_threshold):
        """
        Aggregated information for this measurement

        Returns a dictionary of values:
           label: Short human-readable description of the measurement
           unit (optional): Human-readable description of the measurement unit
           unsafe: True if at least one measurement within the window was outside the defined limits
           warning: True if at least one measurement within the window was in the warning limits
           current: True if the latest measurement was more recent than the stale data threshold
           latest: Latest value for this parameter
           date_start: Date of first measurement aggregated
           date_end: Date of last measurement aggregated
           date_count: Number of measurements aggregated
           limits (optional): Tuple of min and max safe values if defined for this parameter
           warn_limits (optional): Tuple of min and max safe values if defined for this parameter
           min (optional): Minimum aggregated value for Range parameters
           max (optional): Maximum aggregated value for Range parameters
           values (optional): Values seen during the aggregation period for Set parameters
           valid_values (optional): Values that don't trigger an unsafe condition for Set parameters
           format (optional): ID describing what set values mean

        Note that unsafe and warning will be FALSE if there is no data for this measurement,
        so always check current and/or date_count before trying to interpret that flag
        """

        # Discard any measurements that are flagged as ignored
        # This allows "no value" measurements to be not counted as bad
        if self._ignore_values:
            measurements = [m for m in measurements \
                if m[self._measurement_name] not in self._ignore_values]

        measurement_start = measurements[0]['date'] if measurements else datetime.datetime.min
        measurement_end = measurements[-1]['date'] if measurements else datetime.datetime.min

        ret = {
            'label': self._label,
            'unsafe': False,
            'warning': False,
            'current': measurement_end >= stale_measurement_threshold,
            'date_start': measurement_start.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'date_end': measurement_end.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'date_count' : len(measurements),
        }

        if self._unit:
            ret['unit'] = self._unit

        if self._limits:
            ret['limits'] = self._limits

        if self._warn_limits:
            ret['warn_limits'] = self._warn_limits

        if not measurements:
            return ret

        if self._behaviour == AggregateBehaviour.Range:
            ret['min'] = ret['max'] = measurements[0][self._measurement_name]
            for measurement in measurements:
                value = measurement[self._measurement_name]
                ret['min'] = min(value, ret['min'])
                ret['max'] = max(value, ret['max'])
                ret['latest'] = value

            if self._limits:
                ret['unsafe'] = ret['min'] < self._limits[0] or ret['max'] > self._limits[1]

            if self._warn_limits:
                ret['warning'] = ret['min'] < self._warn_limits[0] \
                    or ret['max'] > self._warn_limits[1]

        elif self._behaviour == AggregateBehaviour.Median:
            ret['latest'] = statistics.median([m[self._measurement_name] for m in measurements])
            if self._limits:
                ret['unsafe'] = ret['latest'] < self._limits[0] or ret['latest'] > self._limits[1]

            if self._warn_limits:
                ret['warning'] = ret['latest'] < self._warn_limits[0] \
                    or ret['latest'] > self._warn_limits[1]

        elif self._behaviour == AggregateBehaviour.Set:
            ret['latest'] = measurements[-1][self._measurement_name]

            # Convert to a set to remove duplicates
            values = {m[self._measurement_name] for m in measurements}

            # Convert back to a list so it can be serialized as json
            ret['values'] = list(values)

            if self._display:
                ret['display'] = self._display

            if self._valid_set_values:
                ret['valid_values'] = list(self._valid_set_values)

                # If all values are valid the set difference against _valid_set_values will be empty
                ret['unsafe'] = ret['warning'] = bool(values - self._valid_set_values)

        else:
            ret['latest'] = measurements[-1][self._measurement_name]

            if self._display:
                ret['display'] = self._display

            if self._limits and ret['current']:
                ret['unsafe'] = ret['latest'] < self._limits[0] or ret['latest'] > self._limits[1]

            if self._warn_limits and ret['current']:
                ret['warning'] = ret['latest'] < self._warn_limits[0] \
                    or ret['latest'] > self._warn_limits[1]

        return ret


class FilterInvalidAggregateParameter(AggregateParameter):
    """AggregateParameter subclass for parameters that are paired with a _valid flag"""
    def aggregate(self, measurements, stale_measurement_threshold):
        """Aggregates after discarding measurements that are not valid for this parameter"""
        measurements = [m for m in measurements if m[self._measurement_name + '_valid']]
        return super().aggregate(measurements, stale_measurement_threshold)
