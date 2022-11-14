import json

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from utils.utils import get_config


class CoinmarketcapAPI:
    def __init__(self):
        self.config = get_config().coinmarketcap
        api_type = "sandbox" if self.config.sandbox else "pro"
        self.url = f"https://{api_type}-api.coinmarketcap.com"
        self.api_key = self.config.api_key
        self.session = self.ini_connection()

    def ini_connection(self):
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
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
            response = self.session.get(url, params=parameters)
            data = json.loads(response.text)
            return data
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
