import requests
import pycountry


class Location(object):
    def __init__(self):
        loc = requests.get("https://ipinfo.io").json()

        self._country = pycountry.countries.get(alpha_2=loc['country']).name
        self._region = loc['region']
        self._city = loc['city']

    @property
    def country(self):
        return self._country

    @property
    def region(self):
        return self._region

    @property
    def city(self):
        return self._city

    def __repr__(self):
        return "{}({}, {}, {})".format(self.__class__.__name__, self.city, self.region, self.country)
