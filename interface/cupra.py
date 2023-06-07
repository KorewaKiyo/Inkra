import time
import requests
import yaml

# Terminal interface
from interface.terminal import Terminal


class Cupra:
    """Interface for the MyCupra app backend"""

    def __init__(self):
        # We can expect config.yaml to exist if we got to here from inkra.py
        with open("config.yml", "r") as config_file:
            config = yaml.safe_load(config_file)

        self.config = config.get("Cupra", None)
        if self.config is None:
            raise Terminal.ConfigError("Could not find Cupra section in config.yml")

        self.endpoint = "https://ola.prod.code.seat.cloud.vwgroup.com/"
        self.ua = "CUPRAApp%20-%20Store/20230404 CFNetwork/1390 Darwin/22.0.0"
        self.user_id = self.config.get("User_ID")
        self.vin = self.config.get("VIN")
        self.token = self.config.get("Token")

        self.header = {
            # I don't know the significance of this, but it doesn't hurt
            "x-csrf-token": "123456789123456789123456789123456789",
            "user-agent": "CUPRAApp%20-%20Store/20230404 CFNetwork/1390 Darwin/22.0.0",
            "user-id": self.user_id,
            "authorization": self.token,
        }

        # Same as weather interface, we'll only cache the status request
        # For SoC, Climate, etc. "
        self.last_response = None

    def get_vehicle_status(self):
        url = f"{self.endpoint}v4/users/{self.user_id}/vehicles/{self.vin}/mycar"

        # Get response object from cache if exists and not more than 5 minutes old.
        # Otherwise, make another request and store.
        if self.last_response is None or time.time() - 300 > self.last_response[1]:
            response = requests.get(url, headers=self.header)
        else:
            response = self.last_response[0]

        if response.status_code != 200:
            Terminal.error(f"Request failed, reason was: {response.reason}")
            return None

        self.last_response = (response, time.time())
        battery_status = response.json().get("engines").get("primary")
        charge_status = response.json().get("services").get("charging")
        climate_status = response.json().get("services").get("climatisation")
        return battery_status, charge_status, climate_status
