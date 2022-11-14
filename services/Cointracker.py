import json
import time

from services.CoinmarketcapAPI import CoinmarketcapAPI
from utils.utils import get_db_connector


class Cointracker:
    def __init__(self):
        self.db = get_db_connector()
        self.api = CoinmarketcapAPI()

    def update_coin(self, coin_symbol: str, data: dict):
        data["last_updated"] = time.time()
        self.db.set(f"coin/{coin_symbol.lower()}", json.dumps(data))

    def get_coin(self, coin_symbol: str):
        coin_key = f"coin/{coin_symbol.lower()}"
        if self.db.exists(coin_key):
            return json.loads(self.db.get(coin_key))

    def fill_db(self, coins_data: dict):
        api_data = self.api.get_currency_quotes_latest(list(coins_data.keys()))
        for coin_symbol, coin_amount in coins_data.items():
            data = {"amount": coin_amount, "data": api_data['data'][coin_symbol.upper()][0]}
            self.update_coin(coin_symbol, data)

    def get_portfolio(self):
        coins = self.db.list('coin/*')
        total = 0
        for coin in coins:
            coin_info = self.get_coin(coin.split("coin/")[1])
            coin_name = coin_info['data']['name']
            coin_total = float(coin_info['data']['quote']['USD']['price']) * float(coin_info['amount'])

            print(f"{coin_name}: {round(coin_total, 2)} USD")
            total += coin_total
        print(total)

        # portfolio_total = 1000
        # coins = []
        # portfolio = {"portfolio_total": portfolio_total,
        #              "coins": coins}
        # return portfolio

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


if __name__ == '__main__':
    tracker = Cointracker()

    # from pathlib import Path
    # from utils.utils import load_yml
    # coins = load_yml(Path(__file__).parent / '..' / 'coins.yml')
    # tracker.fill_db(coins)

    tracker.get_portfolio()
