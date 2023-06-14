import requests
import os
import binascii
import hashlib
from bs4 import BeautifulSoup
from requests.models import CaseInsensitiveDict
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from oauthlib.oauth import prepare_grant_uri


class OpenID:
    def __init__(self, username: str = None, password: str = None):
        if username is None or password is None:
            raise

        self.session = requests.session()
        retries = Retry(total=5,
                        backoff_factor=2,
                        status_forcelist=[500],
                        raise_on_status=False)
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.headers = CaseInsensitiveDict({
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
            'accept': '*/*',
            'accept-language': 'de-de',
            'accept-encoding': 'gzip, deflate, br'
        })

        self.client_id = "3c756d46-f1ba-4d78-9f9a-cff0d5292d51@apps_vw-dilab_com"
        self.redirect_uri = "cupra://oauth-callback"

        self.username = username
        self.password = password

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

        auth_response = self.session.get("https://identity.vwgroup.io/oidc/v1/authorize", allow_redirects=False)
        print(auth_response.status_code)
        soup = BeautifulSoup(auth_response.text, 'html.parser')

        # These values associate the authorization requests together, I believe.
        self.csrf = soup.find(id="csrf").attrs.get("value")
        self.hmac = soup.find(id="hmac").attrs.get("value")
        self.relay_state = soup.find(id="input_relayState").attrs.get("value")

        return auth_response

    def signin(self):
        body = {
            "_csrf": self.csrf,
            "relayState": self.relay_state,
            "hmac": self.hmac,
            "email": self.username,

        }
        loginHeaders = self.session.headers.copy()
        loginHeaders[
            "referer"] = f"https://identity.vwgroup.io/signin-service/v1/signin/3c756d46-f1ba-4d78-9f9a-cff0d5292d51" \
                         f"@apps_vw-dilab_com?relayState={self.relay_state}"
        loginHeaders["Content-Type"] = 'application/x-www-form-urlencoded'

        signin_response = self.session.post(
            f"https://identity.vwgroup.io/signin-service/v1/3c756d46-f1ba-4d78-9f9a-cff0d5292d51@apps_vw-dilab_com/login/identifier",
            data=body,
            headers=loginHeaders, allow_redirects=True)
        return signin_response


cupra = OpenID("USERNAME@gmail.com", "PASSWORD")
auth_begin = cupra.begin_auth()
signin = cupra.signin()
