import requests
import geocoder


class Weather:
    def get_coords(self, location):
        latlng = geocoder.arcgis(location).latlng
        return latlng

    def __init__(self, city, country):
        self.coordinates = self.get_coords(f"{city}{country}")
        print(self.coordinates)

    def get_weather(self):
        pass
