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

"""Commandline client for communicating with opsd"""

import datetime
import os
import Pyro4
import sys

DAEMON_URI = 'PYRO:ops_daemon@localhost:9002'

def print_status():
    """Prints the latest status data in human-readable form"""
    status = Pyro4.Proxy(DAEMON_URI).status()

    if status is None:
        print('No data available')
    else:
        green = u'\033[92m'
        red = u'\033[91m'
        yellow = u'\033[93m'
        bold = u'\033[1m'
        clearformat = u'\033[0m'

        time_start = datetime.datetime.strptime(
            status['vaisala_measurement_start'], '%Y-%m-%dT%H:%M:%SZ')
        time_end = datetime.datetime.strptime(
            status['vaisala_measurement_end'], '%Y-%m-%dT%H:%M:%SZ')

        print('It is {}{}{} to observe'.format(
            green+bold if status['can_observe'] else red+bold,
            'SAFE' if status['can_observe'] else 'NOT SAFE', clearformat))
        if not status['vaisala_sufficient_data']:
            print('{}Insufficient external weather history{}'.format(yellow, clearformat))

        print(u'Conditions from {2}{0}{3} \u2014 {2}{1}{3}:'.format(
            time_start.strftime('%H:%M:%S'),
            time_end.strftime('%H:%M:%S'), bold, clearformat))
        print(u'             Wind: {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} km/h'.format(
            status['wind'][0], status['wind'][1],
            green if status['wind'][2] else red, bold, clearformat))
        print(u'         Pressure: {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} hPa'.format(
            status['pressure'][0], status['pressure'][1],
            green if status['pressure'][2] else red, bold, clearformat))
        print(u'    Outside Temp.: {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} \u2103'.format(
            status['vaisala_temp'][0], status['vaisala_temp'][1],
            green if status['vaisala_temp'][2] else red, bold, clearformat))
        print(u'     Outside Hum. {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} %RH'.format(
            status['vaisala_humidity'][0], status['vaisala_humidity'][1],
            green if status['vaisala_humidity'][2] else red, bold, clearformat))
        print()
    return status is None or not status['can_observe']

def print_raw():
    """Prints the latest status data in machine-readable form"""
    status = Pyro4.Proxy(DAEMON_URI).status()
    print(status)
    return status is None or not status['can_observe']

def print_usage(name):
    """Prints the utility help"""
    print('Usage: {} command'.format(name))
    print()
    print('    {} status'.format(name))
    print()
    print('  Print a human-readable summary of the operations status and exit')
    print()
    print('    {} raw'.format(name))
    print()
    print('  Print a machine-readable summary of the operations status and exit')
    print()

    return 1

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'status':
            sys.exit(print_status())
        elif sys.argv[1] == 'raw':
            sys.exit(print_raw())
    else:
        sys.exit(print_usage(os.path.basename(sys.argv[0])))
