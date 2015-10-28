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

import Pyro4

DAEMON_URI = 'PYRO:ops_daemon@localhost:9002'

def print_status():
    """Prints the latest status data in human-readable form"""
    ops = Pyro4.Proxy(DAEMON_URI)
    latest = ops.status()

    if latest is None:
        print('No data available')
    else:
        print(latest)
        print()

if __name__ == '__main__':
    print_status()
