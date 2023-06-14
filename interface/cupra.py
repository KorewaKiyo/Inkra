import time
import requests
import yaml

# Terminal interface
from interface.terminal import Terminal

from weconnect_cupra import weconnect_cupra
from weconnect_cupra.service import Service
from weconnect_cupra.elements.control_operation import ControlOperation
from weconnect_cupra.api.cupra.domain import Domain
from weconnect_cupra.api.cupra.elements.enums import MaximumChargeCurrent, UnlockPlugState


class Cupra:
    """Interface for the MyCupra app backend"""

    def __init__(self):
        # We can expect config.yaml to exist if we got to here from inkra.py
        with open("config.yml", "r") as config_file:
            config = yaml.safe_load(config_file)

        self.config = config.get("Cupra", None)
        if self.config is None:
            raise Terminal.ConfigError("Could not find Cupra section in config.yml")

        self.username = self.config.get("Username")
        self.password = self.config.get("Password")
        self.vin = self.config.get("VIN")

        self.cupra = weconnect_cupra.WeConnect(username=self.username, password=self.password,
                                               updateAfterLogin=True, loginOnInit=True,
                                               service=Service("MYCUPRA"))
        # Same as weather interface, we'll only cache the status request
        # For SoC, Climate, etc. "
        self.last_response = None


        def