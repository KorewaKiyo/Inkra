import requests


class Cupra:
    """Interface for the MyCupra app backend"""

    def __init__(self):
        self.endpoint = "https://ola.prod.code.seat.cloud.vwgroup.com/v4"
        self.ua = 'CUPRAApp%20-%20Store/20230404 CFNetwork/1390 Darwin/22.0.0'
        self.user_id = 3
