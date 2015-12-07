#!/usr/bin/env python3
#
# This file is part of environmentd.
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

import distutils.core

distutils.core.setup(name='onemetre-environmentd',
    version='1.0',
    author="Paul Chote",
    author_email="P.Chote@warwick.ac.uk",
    url="https://github.com/warwick-one-metre/environmentd",
    description="Daemon for exposing recent dome environment conditions via Pyro.",
    long_description="Daemon for exposing recent dome environment conditions via Pyro.",
    license="GPL3",

    options = {'bdist_rpm': {
      'post_install' : 'postinstall.sh',
      'group' : 'Unspecified',
      'requires' : 'python3, onemetre-vaisalad'
    }},

    scripts=['environmentd', 'environment'],
    data_files=[
        ('/usr/lib/systemd/system', ['environmentd.service']),
    ],
)