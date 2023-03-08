import json
import logging
import os

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from cointracker.utils.utils import get_config, get_api_key


class CoinmarketcapAPI:
    def __init__(self):
        self.logger = logging.getLogger("main")
        self.config = get_config().coinmarketcap
        api_type = "sandbox" if self.config.sandbox else "pro"
        self.url = f"https://{api_type}-api.coinmarketcap.com"
        self.api_key = self.config.api_key
        self.session = self.ini_connection()

    def ini_connection(self):
        api_key = get_api_key(api_name="Coinmarketcap")
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': api_key,
        }
        session = Session()
        session.headers.update(headers)

        return session

    def get_currency_quotes_latest(self, symbols: list):
        symbols = ",".join(symbols)
        endpoint = "/v2/cryptocurrency/quotes/latest"
        parameters = {
            'symbol': symbols
        }
        return self.__get(endpoint, parameters)

    def __get(self, endpoint, parameters):
        url = self.url + endpoint
        try:
            self.logger.debug(f"Making request to {url}")
            response = self.session.get(url, params=parameters)
            data = json.loads(response.text)
            return data
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            self.logger.error(e)
