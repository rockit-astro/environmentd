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
        bold = u'\033[1m'
        clearformat = u'\033[0m'

        vaisala_start = datetime.datetime.strptime(
            status['vaisala_measurement_start'], '%Y-%m-%dT%H:%M:%SZ')
        vaisala_end = datetime.datetime.strptime(
            status['vaisala_measurement_end'], '%Y-%m-%dT%H:%M:%SZ')

        roomalert_start = datetime.datetime.strptime(
            status['roomalert_measurement_start'], '%Y-%m-%dT%H:%M:%SZ')
        roomalert_end = datetime.datetime.strptime(
            status['roomalert_measurement_end'], '%Y-%m-%dT%H:%M:%SZ')

        print('It is {}{}{} to observe'.format(
            green+bold if status['can_observe'] else red+bold,
            'SAFE' if status['can_observe'] else 'NOT SAFE', clearformat))
        print()

        print(u'Vaisala data from {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4}:'.format(
            vaisala_start.strftime('%H:%M:%S'), vaisala_end.strftime('%H:%M:%S'),
            green if status['vaisala_sufficient_data'] else red, bold, clearformat))
        print(u'             Wind: {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} km/h'.format(
            status['wind'][0], status['wind'][1],
            green if status['wind'][2] else red, bold, clearformat))
        print(u'         Pressure: {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} hPa'.format(
            status['pressure'][0], status['pressure'][1],
            green if status['pressure'][2] else red, bold, clearformat))
        print(u'   N2 Plant Temp.: {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} \u2103'.format(
            status['vaisala_temp'][0], status['vaisala_temp'][1],
            green if status['vaisala_temp'][2] else red, bold, clearformat))
        print(u'    N2 Plant Hum.: {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} %RH'.format(
            status['vaisala_humidity'][0], status['vaisala_humidity'][1],
            green if status['vaisala_humidity'][2] else red, bold, clearformat))
        print()

        print(u'RoomAlert data from {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4}:'.format(
            roomalert_start.strftime('%H:%M:%S'), roomalert_end.strftime('%H:%M:%S'),
            green if status['roomalert_sufficient_data'] else red, bold, clearformat))
        print(u'    Outside Temp.: {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} \u2103'.format(
            status['external_temp'][0], status['external_temp'][1],
            green if status['external_temp'][2] else red, bold, clearformat))
        print(u'     Outside Hum.: {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} %RH'.format(
            status['external_humidity'][0], status['external_humidity'][1],
            green if status['external_humidity'][2] else red, bold, clearformat))
        print(u'   Internal Temp.: {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} \u2103'.format(
            status['internal_temp'][0], status['internal_temp'][1],
            green if status['internal_temp'][2] else red, bold, clearformat))
        print(u'    Internal Hum.: {2}{3}{0}{4}{2} \u2014 {2}{3}{1}{4} %RH'.format(
            status['internal_humidity'][0], status['internal_humidity'][1],
            green if status['internal_humidity'][2] else red, bold, clearformat))

        print(u'      Truss Temp.: {0} \u2014 {1} \u2103'.format(
            status['truss_temp'][0], status['truss_temp'][1]))
        print(u'     Server Temp.: {0} \u2014 {1} \u2103'.format(
            status['roomalert_temp'][0], status['roomalert_temp'][1]))
        print(u'      Server Hum.: {0} \u2014 {1} %RH'.format(
            status['roomalert_humidity'][0], status['roomalert_humidity'][1]))

        hatch = ""
        if True in status['hatch_open']:
            hatch += "OPEN"
        if False in status['hatch_open']:
            if len(hatch) > 0:
                hatch += ", "
            hatch += "CLOSED"

        trap = ""
        if True in status['trap_open']:
            trap += "OPEN"
        if False in status['trap_open']:
            if len(trap) > 0:
                trap += ", "
            trap += "CLOSED"

        print(u'       Side Hatch: '+hatch)
        print(u'        Trap Door: '+trap)
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
