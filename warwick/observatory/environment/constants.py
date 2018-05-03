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

class CommandStatus:
    """Return codes for ResetParameterStatus"""
    Success = 0
    InvalidControlIP = 10

    InvalidWatcher = 11
    InvalidParameter = 12

    _messages = {
        # General error codes
        10: 'error: command not accepted from this IP',
        -100: 'error: terminated by user',
        -101: 'error: unable to communicate with environment daemon'
    }

    @classmethod
    def message(cls, error_code):
        """Returns a human readable string describing an error code"""
        if error_code in cls._messages:
            return cls._messages[error_code]
        return 'error: Unknown error code {}'.format(error_code)
