import requests
import geocoder


class Weather:

    def __init__(self, city, country):
        self.city = city
        self.country = country

    def get_coords(self, location):
        latlng = geocoder.arcgis(address).latlng
        return latlng

    def get_weather(self, location):
        latlng = self.get_coords(location)
