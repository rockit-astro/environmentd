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

"""Constants and status codes used by environmentd"""

# pylint: disable=too-few-public-methods

class DisableParameterStatus:
    """Return codes for ResetParameterStatus"""
    Success, InvalidWatcher, InvalidParameter = range(3)

class ParameterStatus:
    """Status of a measurement parameter"""
    Unsafe, Safe, Disabled = range(3)
