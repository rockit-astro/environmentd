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

"""Helper function to validate and parse the json config file"""

# pylint: disable=broad-except
# pylint: disable=too-few-public-methods

import json
import sys
import traceback
import jsonschema

from warwick.observatory.common import daemons, IP

from .aggregate_parameter import (
    AggregateBehaviour,
    AggregateParameter,
    FilterInvalidAggregateParameter)
from .pyro_watcher import PyroWatcher

CONFIG_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['daemon', 'log_name', 'window_length', 'control_machines', 'watchers'],
    'properties': {
        'daemon': {
            'type': 'string',
            'daemon_name': True
        },
        'log_name': {
            'type': 'string',
        },
        'window_length': {
            'type': 'number',
            'minimum': 1,
            'maximum': 86400
        },
        'control_machines': {
            'type': 'array',
            'items': {
                'type': 'string',
                'machine_name': True
            }
        },
        'watchers': {
            'type': 'object',
            'additionalProperties': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['label', 'daemon', 'query_rate', 'stale_age', 'parameters'],
                'properties': {
                    'label': {
                        'type': 'string',
                    },
                    'daemon': {
                        'type': 'string',
                        'daemon_name': True
                    },
                    'query_rate': {
                        'type': 'number',
                        'minimum': 1,
                        'maximum': 86400
                    },
                    'stale_age': {
                        'type': 'number',
                        'minimum': 1,
                        'maximum': 86400
                    },
                    'parameters': {
                        'type': 'object',
                        'additionalProperties': {
                            'type': 'object',
                            'additionalProperties': False,
                            'required': ['label', 'type'],
                            'properties': {
                                'label': {
                                    'type': 'string',
                                },
                                'unit': {
                                    'type': 'string',
                                },
                                'type': {
                                    'type': 'string',
                                    # These must also be defined in the 'anyOf' cases below
                                    'enum': ['Range', 'Median', 'Latest', 'Set']
                                },
                                'filter_invalid': {
                                    'type': 'boolean'
                                },
                                'warn_limits': {
                                    'type': 'array',
                                    'maxItems': 2,
                                    'minItems': 2,
                                    'items': {
                                        'type': 'number'
                                    }
                                },
                                'unsafe_limits': {
                                    'type': 'array',
                                    'maxItems': 2,
                                    'minItems': 2,
                                    'items': {
                                        'type': 'number'
                                    }
                                },
                                'display': {
                                    'type': 'string',
                                    'enum': ['UPSStatus', 'BoolClosedOpen', 'BoolSafeTripped',
                                             'BoolHealthyUnhealthy', 'BoolPowerOnOff', 'DiskBytes']
                                },
                                # Only used if type: Median
                                'median_key': {
                                    'type': 'string'
                                },

                                # Only used if type: Set
                                'valid_set_values': {
                                    'type': 'array'
                                }
                            },
                            # Require 'median_key' if 'type' is a median
                            'anyOf': [
                                {
                                    'properties': {
                                        'type': {
                                            'enum': ['Median']
                                        }
                                    },
                                    'required': ['median_key']
                                },
                                {
                                    'properties': {
                                        'type': {
                                            'enum': ['Set', 'Range', 'Latest']
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
}


class ConfigSchemaViolationError(Exception):
    """Exception used to report schema violations"""
    def __init__(self, errors):
        message = 'Invalid configuration:\n\t' + '\n\t'.join(errors)
        super(ConfigSchemaViolationError, self).__init__(message)


def __create_validator():
    """Returns a template validator that includes support for the
       custom schema tags used by the observation schedules:
            daemon_name: add to string properties to require they match an entry in the
                         warwick.observatory.common.daemons address book
            machine_name: add to string properties to require they match an entry in the
                         warwick.observatory.common.IP address book
    """
    validators = dict(jsonschema.Draft4Validator.VALIDATORS)

    # pylint: disable=unused-argument
    def daemon_name(validator, value, instance, schema):
        """Validate a string as a valid daemon name"""
        try:
            getattr(daemons, instance)
        except Exception:
            yield jsonschema.ValidationError('{} is not a valid daemon name'.format(instance))

    def machine_name(validator, value, instance, schema):
        """Validate a string as a valid machine name"""
        try:
            getattr(IP, instance)
        except Exception:
            yield jsonschema.ValidationError('{} is not a valid machine name'.format(instance))
    # pylint: enable=unused-argument

    validators['daemon_name'] = daemon_name
    validators['machine_name'] = machine_name
    return jsonschema.validators.create(meta_schema=jsonschema.Draft4Validator.META_SCHEMA,
                                        validators=validators)


def validate_config(config_json):
    """Tests whether a json object defines a valid environment config file
       Raises SchemaViolationError on error
    """
    errors = []
    try:
        validator = __create_validator()
        for error in sorted(validator(CONFIG_SCHEMA).iter_errors(config_json),
                            key=lambda e: e.path):
            if error.path:
                path = '->'.join([str(p) for p in error.path])
                message = path + ': ' + error.message
            else:
                message = error.message
            errors.append(message)
    except Exception:
        traceback.print_exc(file=sys.stdout)
        errors = ['exception while validating']

    if errors:
        raise ConfigSchemaViolationError(errors)


def parse_watcher_parameter(parameter, parameter_json):
    """Parse an *AggregateParameter from a json config block"""
    parameter_type = AggregateParameter
    if 'filter_invalid' in parameter_json and parameter_json['filter_invalid']:
        parameter_type = FilterInvalidAggregateParameter

    behaviour = AggregateBehaviour.parse(parameter_json['type'])
    median_key = None
    if behaviour == AggregateBehaviour.Median and 'median_key' in parameter_json:
        median_key = parameter_json['median_key']

    valid_set_values = None
    if behaviour == AggregateBehaviour.Set and 'valid_set_values' in parameter_json:
        valid_set_values = set(parameter_json['valid_set_values'])

    limits = parameter_json.get('unsafe_limits', None)
    warn_limits = parameter_json.get('warn_limits', None)
    unit = parameter_json.get('unit', None)
    display = parameter_json.get('display', None)

    return parameter_type(parameter, behaviour, parameter_json['label'], unit=unit,
                          limits=limits,
                          warn_limits=warn_limits,
                          measurement_name=median_key,
                          valid_set_values=valid_set_values,
                          display=display)

class Config:
    """Daemon configuration parsed from a json file"""
    def __init__(self, config_filename):
        # Will throw on file not found or invalid json
        with open(config_filename, 'r') as config_file:
            config_json = json.load(config_file)

        # Will throw on schema violations
        validate_config(config_json)

        self.daemon = getattr(daemons, config_json['daemon'])
        self.log_name = config_json['log_name']
        self.control_ips = [getattr(IP, machine) for machine in config_json['control_machines']]
        self.window_length = config_json['window_length']

        self.watcher_config = []
        for watcher, watcher_json in config_json['watchers'].items():
            self.watcher_config.append({
                'name': watcher,
                'daemon': getattr(daemons, watcher_json['daemon']),
                'label': watcher_json['label'],
                'query_rate': watcher_json['query_rate'],
                'stale_age': watcher_json['stale_age'],
                'parameters': [parse_watcher_parameter(k, v)
                               for (k, v) in watcher_json['parameters'].items()],
            })

    def get_watchers(self):
        """Returns a list of PyroWatchers to be monitored"""
        def create_watcher(config):
            return PyroWatcher(config['name'], config['daemon'], config['label'],
                               config['query_rate'], config['stale_age'], self.window_length,
                               config['parameters'], self.log_name)

        return [create_watcher(w) for w in self.watcher_config]
