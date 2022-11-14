from pprint import pprint

from services.CoinmarketcapAPI import CoinmarketcapAPI

api = CoinmarketcapAPI()
symbols = ['btc', 'eth']
pprint(api.get_currency_quotes_latest(symbols))
