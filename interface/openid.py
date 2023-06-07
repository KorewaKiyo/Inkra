import requests
import os
import binascii
import hashlib
from bs4 import BeautifulSoup


class OpenID:
    def __init__(self):  # , username, password):
        self.session = requests.session()

        self.client_id = "3c756d46-f1ba-4d78-9f9a-cff0d5292d51@apps_vw-dilab_com"
        self.redirect_uri = "cupra://oauth-callback"

        # Random hex string for CSRF token
        self.state = binascii.b2a_hex(os.urandom(16)).upper()

        # I think getting this from VW is important
        self.csrf = None
        self.hmac = None
        self.relay_state = None

    def begin_auth(self):
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid profile nickname birthdate phone",
            "state": self.state,
            "ui_locales": "en",
            "code_challenge_method": "S256",

            # I really am not sure what this hash is expected to be.
            "code_challenge": hashlib.sha256(self.state)
        }

        response = requests.get("https://identity.vwgroup.io/oidc/v1/authorize", params)
        soup = BeautifulSoup(response.text, 'html.parser')

        # These values associate the authorization requests together, I believe.
        self.csrf = soup.find(id="csrf").attrs.get("value")
        self.hmac = soup.find(id="hmac").attrs.get("value")
        self.relay_state = soup.find(id="input_relayState").attrs.get("value")

        return response

    def signing

cupra = OpenID()
response = cupra.begin_auth()
