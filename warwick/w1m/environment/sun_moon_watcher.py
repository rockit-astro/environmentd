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

"""Class used for calculating sun and moon data"""

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=broad-except

import datetime
from astropy.coordinates import (
    get_sun,
    EarthLocation,
    AltAz
)
from astropy.time import Time
from astropy import units as u
import ephem

# Measured from GPS receiver
SITE_LATITUDE = 28.7603135
SITE_LONGITUDE = -17.8796168
SITE_ELEVATION = 2387

SUN_ELEVATION_LIMIT = -2
SUN_ELEVATION_WARNING = -10

class SunMoonWatcher:
    """Calculates sun and moon data"""
    def __init__(self, daemon_name):
        self.daemon_name = daemon_name
        # pylint: disable=no-member
        self._lapalma = EarthLocation(lat=SITE_LATITUDE*u.deg,
                                      lon=SITE_LONGITUDE*u.deg,
                                      height=SITE_ELEVATION*u.m)
        # pylint: enable=no-member
        self._obs = ephem.Observer()
        # pylint: disable=assigning-non-slot
        self._obs.lat = SITE_LATITUDE*ephem.degree
        self._obs.lon = SITE_LONGITUDE*ephem.degree
        self._obs.elev = SITE_ELEVATION
        # pylint: enable=assigning-non-slot

    def status(self):
        """Returns a dictionary of current sun and moon state"""
        now_date = datetime.datetime.utcnow()
        now_str = now_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        now_time = Time(now_date, format='datetime', scale='utc')
        frame = AltAz(obstime=now_time, location=self._lapalma)
        sun = get_sun(now_time).transform_to(frame)

        # pylint: disable=assigning-non-slot
        self._obs.date = now_date
        # pylint: enable=assigning-non-slot
        moon = ephem.Moon(self._obs.date)
        moon.compute(self._obs)

        return {
            'sun_alt': {
                'current': True,
                'date_start': now_str,
                'date_end': now_str,
                'date_count': 1,
                'latest': sun.alt.value,
                'limits': [-90, SUN_ELEVATION_LIMIT],
                'warn_limits': [-90, SUN_ELEVATION_WARNING],
                'unsafe': sun.alt.value >= SUN_ELEVATION_LIMIT,
                'warning': sun.alt.value >= SUN_ELEVATION_WARNING,
            },

            'moon_phase': {
                'current': True,
                'date_start': now_str,
                'date_end': now_str,
                'date_count': 1,
                'latest': moon.phase,
                'unsafe': False,
                'warning': False
            },

            'moon_alt': {
                'current': True,
                'date_start': now_str,
                'date_end': now_str,
                'date_count': 1,
                'latest': moon.alt/ephem.degree,
                'unsafe': False,
                'warning': False
            }
        }

    def clear_history(self):
        """Clear the cached measurements"""
        pass
