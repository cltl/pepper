import requests
import pycountry
import platform
import subprocess
import os
import re
import reverse_geocoder
from random import getrandbits

from typing import Optional, Tuple


class Location(object):
    """Location on Earth"""

    UNKNOWN = "Unknown"

    def __init__(self):
        # TODO use UUIDs
        self._id = getrandbits(128)
        self._label = self.UNKNOWN

        try:
            loc = requests.get("https://ipinfo.io").json()

            self._country = pycountry.countries.get(alpha_2=loc['country']).name
            self._region = loc['region']
            self._city = loc['city']
        except:
            self._country = self.UNKNOWN
            self._region = self.UNKNOWN
            self._city = self.UNKNOWN

    @property
    def id(self):
        # type: () -> int
        """
        ID for this Location object

        Returns
        -------
        id: int
        """
        return self._id

    @property
    def country(self):
        # type: () -> str
        """
        Country String

        Returns
        -------
        country: str
        """
        return self._country

    @property
    def region(self):
        # type: () -> str
        """
        Region String

        Returns
        -------
        region: str
        """
        return self._region

    @property
    def city(self):
        # type: () -> str
        """
        City String

        Returns
        -------
        city: str
        """
        return self._city

    @property
    def label(self):
        # type: () -> str
        """
        Learned Location Label

        Returns
        -------
        label: str
        """
        return self._label

    @label.setter
    def label(self, value):
        # type: (str) -> None
        """
        Learned Location Label

        Parameters
        ----------
        value: str
        """
        self._label = value

    @staticmethod
    def _get_lat_lon():
        # type: () -> Optional[Tuple[float, float]]
        """
        Get Latitude & Longitude from GPS

        Returns
        -------
        latlon: Optional[Tuple[float, float]]
            GPS Latitude & Longitude
        """
        try:
            if platform.system() == "Darwin":
                # Use WhereAmI tool by Rob Mathers -> https://github.com/robmathers/WhereAmI
                whereami = os.path.join(os.path.dirname(__file__), 'util', 'whereami')
                regex = "Latitude: (.+?)\nLongitude: (.+?)\n"
                return tuple(float(coord) for coord in re.findall(regex, subprocess.check_output(whereami))[0])
            else:
                raise Exception()
        except:  # TODO: Add Support for (at least) Windows
            print("Couldn't get GPS Coordinates")
            return None

    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, self.city, self.region, self.country)


if __name__ == '__main__':
    latlon = Location._get_lat_lon()
    result = reverse_geocoder.search(latlon, verbose=False)
    print(result, latlon)
