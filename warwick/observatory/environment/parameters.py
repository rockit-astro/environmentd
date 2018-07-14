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

from .aggregate_parameter import (
    AggregateBehaviour,
    AggregateParameter,
    FilterInvalidAggregateParameter)

# pylint: disable=too-few-public-methods

def build_parameter_list(parameter_type, params, limits, warn_limits):
    """Builds a PyroWatcher parameter list"""
    parameter_list = []
    limits = limits or {}
    warn_limits = warn_limits or {}
    for key, value in params.items():
        if isinstance(value, dict):
            param = parameter_type(key, value.get('behaviour'), limits=limits.get(key),
                                   warn_limits=warn_limits.get(key),
                                   valid_set_values=value.get('valid_set_values'),
                                   measurement_name=value.get('name'))
        else:
            param = parameter_type(key, value, limits=limits.get(key),
                                   warn_limits=warn_limits.get(key))

        parameter_list.append(param)
    return parameter_list

def vaisala_parameters(limits, warn_limits):
    """Returns a PyroWatcher parameter list for monitoring a vaisalad instance"""
    params = {
        'wind_speed': AggregateBehaviour.Range,
        'median_wind_speed': {'name': 'wind_speed', 'behaviour': AggregateBehaviour.Median},
        'temperature': AggregateBehaviour.Range,
        'relative_humidity': AggregateBehaviour.Range,
        'pressure': AggregateBehaviour.Range,
        'accumulated_rain': AggregateBehaviour.Range,
        'dew_point_delta': AggregateBehaviour.Range
    }

    return build_parameter_list(FilterInvalidAggregateParameter, params, limits, warn_limits)

def onemetre_roomalert_parameters(limits, warn_limits):
    """Returns a PyroWatcher parameter list for monitoring the w1m roomalertd instance"""
    params = {
        'internal_temp': AggregateBehaviour.Range,
        'internal_humidity': AggregateBehaviour.Range,
        'roomalert_temp': AggregateBehaviour.Range,
        'roomalert_humidity': AggregateBehaviour.Range,
        'truss_temp': AggregateBehaviour.Range,
        'hatch_closed': AggregateBehaviour.Set,
        'trap_closed': AggregateBehaviour.Set,
        'security_system_safe': AggregateBehaviour.Latest
    }

    return build_parameter_list(AggregateParameter, params, limits, warn_limits)

def goto_roomalert_parameters(limits, warn_limits):
    """Returns a PyroWatcher parameter list for monitoring the goto roomalertd instance"""
    params = {
        'internal_temp': AggregateBehaviour.Range,
        'internal_humidity': AggregateBehaviour.Range,
        'dome2_internal_temp': AggregateBehaviour.Range,
        'dome2_internal_humidity': AggregateBehaviour.Range,
        'roomalert_temp': AggregateBehaviour.Range,
        'roomalert_humidity': AggregateBehaviour.Range,
    }

    return build_parameter_list(AggregateParameter, params, limits, warn_limits)

def superwasp_parameters(limits, warn_limits):
    """Returns a PyroWatcher parameter list for monitoring the superwaspd instance"""
    params = {
        'wind_speed': AggregateBehaviour.Range,
        'median_wind_speed': {'name': 'wind_speed', 'behaviour': AggregateBehaviour.Median},
        'sky_temp': AggregateBehaviour.Range,
        'ext_temperature': AggregateBehaviour.Range,
        'ext_humidity': AggregateBehaviour.Range,
        'dew_point_delta': AggregateBehaviour.Range
    }

    return build_parameter_list(AggregateParameter, params, limits, warn_limits)

def tng_parameters(limits=None, warn_limits=None):
    """Returns a PyroWatcher parameter list for monitoring the tngd instance"""
    params = {
        'dust': AggregateBehaviour.Latest,
        'solarimeter': AggregateBehaviour.Latest,
        'seeing': AggregateBehaviour.Latest
    }

    return build_parameter_list(FilterInvalidAggregateParameter, params, limits, warn_limits)

def diskspace_parameters(limits=None, warn_limits=None):
    """Returns a PyroWatcher parameter list for monitoring a diskspaced instance"""
    params = {
        'data_fs_available_bytes': AggregateBehaviour.Latest,
        'data_fs_percent_available': AggregateBehaviour.Latest
    }

    return build_parameter_list(AggregateParameter, params, limits, warn_limits)

def netping_parameters(limits=None, warn_limits=None):
    """Returns a PyroWatcher parameter list for monitoring the netpingd instance"""
    params = {
        'google': {'behaviour': AggregateBehaviour.Latest, 'ignore': [-1]},
        'ngtshead': {'behaviour': AggregateBehaviour.Latest, 'ignore': [-1]}
    }

    return build_parameter_list(AggregateParameter, params, limits, warn_limits)

def onemetre_power_parameters(limits, warn_limits):
    """Returns a PyroWatcher parameter list for monitoring the w1m powerd instance"""
    params = {
        'main_ups_status': {'behaviour': AggregateBehaviour.Set, 'valid_set_values': set([2])},
        'main_ups_battery_healthy': AggregateBehaviour.Set,
        'main_ups_battery_remaining': AggregateBehaviour.Range,
        'light': AggregateBehaviour.Set
    }

    return build_parameter_list(AggregateParameter, params, limits, warn_limits)

def rasa_power_parameters(limits, warn_limits):
    """Returns a PyroWatcher parameter list for monitoring the w1m powerd instance"""
    params = {
        'ups_status': {'behaviour': AggregateBehaviour.Set, 'valid_set_values': set([2])},
        'ups_battery_healthy': AggregateBehaviour.Set,
        'ups_battery_remaining': AggregateBehaviour.Range,
    }

    return build_parameter_list(AggregateParameter, params, limits, warn_limits)
