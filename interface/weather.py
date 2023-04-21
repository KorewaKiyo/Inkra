import requests
import geocoder

from .terminal import Terminal


class Weather:
    @classmethod
    def get_coords(self, location):
        geo_result = geocoder.arcgis(location)
        if geo_result.ok:
            Terminal.debug(geo_result)
            latlng = geo_result.latlng
            Terminal.debug(latlng)
            return latlng
        else:
            raise RuntimeError

    def __init__(self, city, country):
        self.coordinates = self.get_coords(f"{city}{country}")
        self.endpoint = "https://api.open-meteo.com/v1"

    def get_weather(self):
        params = {
            "latitude": self.coordinates[0],
            "longitude": self.coordinates[1]
        }
