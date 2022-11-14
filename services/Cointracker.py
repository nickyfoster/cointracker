from services.CoinmarketcapAPI import CoinmarketcapAPI
from utils.utils import get_db_connector




class Cointracker:
    def __init__(self):
        self.db = get_db_connector()
        self.api = CoinmarketcapAPI()


    def get_portfolio(self):


'''

data:

{
total holdings in usd

coins:
    name
    price
    price change (1h,6h etc)
    holdings in USD
    amount of coins
}


'''
