import requests
import geocoder
import time
from .terminal import Terminal
from PIL import Image


class Weather:
    @staticmethod
    def weather_code(code):
        short_keywords = {
            0: "clear",
            3: "overcast",
            40: "fog",
            50: "drizzle",
            60: "rain",
            70: "snow",
            80: "showers",
            85: "snow",
            90: "thunder",
        }
        long_keywords = {
            code: keyword
            for start_code, keyword in short_keywords.items()
            for code in range(start_code, start_code + 10)
        }

        if code in long_keywords:
            return long_keywords[code]
        else:
            return Terminal.error("Code not found")

    @classmethod
    def get_coords(cls, location):
        geo_result = geocoder.arcgis(location)
        if geo_result.ok:
            latlng = geo_result.latlng
            return latlng
        else:
            raise RuntimeError

    def __init__(self, city, country):
        self.coordinates = self.get_coords(f"{city}{country}")
        self.endpoint = "https://api.open-meteo.com/v1/forecast"

        self.last_request = None
        self.cached_weather = None

    def weather_icon(self, keyword):
        # if keyword == "overcast":
        icon = Image.open("assets/overcast.png")
        return icon

    def get_weather(self):
        params = {
            "latitude": self.coordinates[0],
            "longitude": self.coordinates[1],
            "current_weather": "True",
        }

        if (
            self.last_request is None
            or time.gmtime().tm_hour > self.last_request.tm_hour
        ):
            response = requests.get(self.endpoint, params)
        else:
            response = self.cached_weather

        if response.status_code == 200:
            self.last_request = time.gmtime()
            self.cached_weather = response
        else:
            Terminal.error(f"Error in response: {response.json()}")
            return None

        # TODO: Implement caching.
        # Terminal.debug(self.last_request)

        keyword = self.weather_code(response.json()["current_weather"]["weathercode"])
        current = response.json()["current_weather"]
        weather = {
            "condition": keyword,
            "temperature": f"{current['temperature']}°C",
            "daytime": current["is_day"],
            "icon": self.weather_icon(keyword),
        }

        return weather
