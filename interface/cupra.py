import yaml
from weconnect_cupra import weconnect_cupra
from weconnect_cupra.service import Service

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

        self.username = self.config.get("Username")
        self.password = self.config.get("Password")
        self.vin = self.config.get("VIN")

        self.cupra_api = weconnect_cupra.WeConnect(
            username=self.username,
            password=self.password,
            maxAge=300,
            tokenfile="token.txt",
            updateAfterLogin=True,
            loginOnInit=True,
            service=Service("MyCupra"),
        )

        self.cupra_api.persistTokens()

        # If the VIN hasn't been defined, but login succeeded,
        # We can grab the first vehicle's VIN from the account and use that
        if self.vin is None:
            self.vin = str(self.cupra_api.vehicles.children[0].vin)

        # Same as weather interface, we'll only cache the status request
        # For SoC, Climate, etc. "
        self.last_response = None

    def get_battery_status(self):
        status = (
            self.cupra_api.vehicles.get(self.vin)
            .domains.get("charging", [])
            .get("batteryStatus")
        )
        if status is not None:
            return status
        else:
            raise
