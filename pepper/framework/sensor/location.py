import requests
import pycountry
import platform
import subprocess
import os
import re
import reverse_geocoder
from random import getrandbits


class Location(object):

    UNKNOWN = "Unknown"

    def __init__(self):
        loc = requests.get("https://ipinfo.io").json()

        self._id = getrandbits(128)

        self._country = pycountry.countries.get(alpha_2=loc['country']).name
        self._region = loc['region']
        self._city = loc['city']
        self._label = self.UNKNOWN

    @property
    def id(self):
        return self._id

    @property
    def country(self):
        return self._country

    @property
    def region(self):
        return self._region

    @property
    def city(self):
        return self._city

    @property
    def label(self):
        return self._label

    @staticmethod
    def _get_lat_lon():
        try:
            if platform.system() == "Darwin":
                # Use WhereAmI tool by Rob Mathers -> https://github.com/robmathers/WhereAmI
                whereami = os.path.join(os.path.dirname(__file__), 'util', 'whereami')
                regex = "Latitude: (.+?)\nLongitude: (.+?)\n"
                return tuple(float(coord) for coord in re.findall(regex, subprocess.check_output(whereami))[0])
            else:
                raise Exception()
        except:
            print("Couldn't get GPS Coordinates")
            return None

    def set_label(self, label):
        self._label = label

    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, self.city, self.region, self.country)


if __name__ == '__main__':
    latlon = Location._get_lat_lon()
    result = reverse_geocoder.search(latlon, verbose=False)
    print(result, latlon)