import yaml
from weconnect_cupra import weconnect_cupra
from weconnect_cupra.service import Service

from PIL import Image

# Terminal interface
from interface.terminal import Terminal

import logging

logger = logging.getLogger("Inkra")


class Cupra:
    """Interface for the MyCupra app backend"""

    def __init__(self):
        # It's expected config.yml exists if execution reaches this far
        with open("config.yml", "r") as config_file:
            config = yaml.safe_load(config_file)

        # It's not expected that config.yml is formatted correctly though
        self.config = config.get("Cupra", None)
        if self.config is None:
            raise Terminal.ConfigError("Could not find Cupra section in config.yml")

        self.username = self.config.get("Username")
        self.password = self.config.get("Password")
        self.vin = self.config.get("VIN")

        self.cupra_api = weconnect_cupra.WeConnect(
            username=self.username,
            password=self.password,
            maxAge=300,
            tokenfile="token.json",
            updateAfterLogin=False,
            service=Service("MyCupra"),
        )
        if self.cupra_api.session.token is None:
            self.cupra_api.login()
            self.cupra_api.persistTokens()
        self.cupra_api.update()

        # If the VIN hasn't been defined, but login succeeded,
        # We can grab the first vehicle's VIN from the account and use that
        if self.vin is None:
            self.cupra_api.update()
            self.vin = str(self.cupra_api.vehicles.children[0].vin)
            logger.info(f"Your VIN is {self.vin}, you should add this to the Cupra section of config.yml")

        # Same as weather interface, we'll only cache the status request
        # For SoC, Climate, etc. "
        self.last_response = None

    @staticmethod
    def __battery_icon(charge: int):
        # TODO: I'm not sure I like this.
        if charge < 0:
            raise AttributeError("Battery can not be less than 0%!")
        elif charge <= 15:
            icon = Image.open("assets/battery15.png")
        elif charge < 30:
            icon = Image.open("assets/battery30.png")
        elif charge < 50:
            icon = Image.open("assets/battery50.png")
        elif charge < 70:
            icon = Image.open("assets/battery70.png")
        else:
            icon = Image.open("assets/battery100.png")
        return icon

    def get_battery_status(self):
        status = (
            self.cupra_api.vehicles.get(self.vin)
            .domains.get("charging", [])
            .get("batteryStatus")
        )
        if status is not None:
            soc_icon = self.__battery_icon(status.currentSOC_pct.value)
            return status, soc_icon
        else:
            return None

    def get_climate_Status(self):
        climate_status = (
            self.cupra_api.vehicles.get(self.vin)
            .domains
            .get("climatisation")
        )
        return climate_status
