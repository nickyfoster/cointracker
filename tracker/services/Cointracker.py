import json
import time
from datetime import datetime

from tabulate import tabulate

from tracker.services.CoinmarketcapAPI import CoinmarketcapAPI
from tracker.utils.utils import get_db_connector, update_nested_dict, prepare_coin_data


class Cointracker:
    def __init__(self):
        self.db = get_db_connector()
        self.api = CoinmarketcapAPI()

    def set_coin_data(self, coin_symbol: str, data: dict):
        data["last_updated"] = time.time()
        self.db.set(f"coin/{coin_symbol.lower()}", json.dumps(data))

    def get_coin_data(self, coin_symbol: str):
        coin_key = f"coin/{coin_symbol.lower()}"
        if self.db.exists(coin_key):
            return json.loads(self.db.get(coin_key))
        else:
            return dict()

    def update_coins_data(self, coins: list):
        api_data = self.api.get_currency_quotes_latest(coins)
        for _coin_symbol in coins:
            current_data = self.get_coin_data(_coin_symbol)
            res_data = update_nested_dict(current_data, api_data['data'][_coin_symbol.upper()][0])
            self.set_coin_data(_coin_symbol, res_data)

    def update_all_coins(self):
        self.update_coins_data(self.list_coins())

    def update_coin_amount(self, coin_symbol: str, amount: float):
        data = self.get_coin_data(coin_symbol)
        data["amount"] = str(amount)
        self.set_coin_data(coin_symbol, data)

    def add_coin(self, coin_symbol: str, amount: float):
        self.set_coin_data(coin_symbol, {"amount": str(amount)})
        self.update_coins_data([coin_symbol])

    def delete_coin(self, coin_symbol):
        self.db.delete_key(f"coin/{coin_symbol.lower()}")

    def list_coins(self):
        coins = self.db.list("coin/*")
        res = list()
        for coin in coins:
            res.append(coin.split('coin/')[1])
        return res

    def fill_db(self, coins_raw_data: dict):
        for coin_name, coin_amount in coins_raw_data.items():
            self.update_coin_amount(coin_name, float(coin_amount))

    def get_portfolio_data(self):
        coins_symbols = self.list_coins()
        result = dict()
        for coin_symbol in coins_symbols:
            data = self.get_coin_data(coin_symbol)
            result[coin_symbol] = data
        return result

    def get_portfolio_price(self):
        portfolio_data = self.get_portfolio_data()
        result = dict()
        portfolio_price = 0
        last_update_time = 0

        for coin_symbol, coin_data in portfolio_data.items():
            last_update_time += float(coin_data["last_updated"])
            portfolio_price += float(coin_data['quote']['USD']['price']) * float(coin_data['amount'])
        result["last_updated"] = last_update_time / len(portfolio_data)
        result["portfolio_price"] = round(portfolio_price, 2)
        return result

    # def get_portfolio_description_str(self):
    #     data = prepare_coin_data(self.get_portfolio_data())
    #     coin_data_str = ""
    #     last_updated = datetime.fromtimestamp(data["last_updated"]).strftime('%Y-%m-%d %H:%M:%S')
    #
    #     for coin_symbol, data in data.items():
    #         if coin_symbol == "last_updated":
    #             continue
    #         coin_data_str += "{0:5} | {1} ({2} %) | {3}$ ({4})\n".format(
    #             coin_symbol, data['price'], data['change_24h'], data['holdings_price'], data['holdings_amount'])
    #     reply_text = f"COIN_NAME | PRICE | AMOUNT\n{coin_data_str}\nLast updated: {last_updated}"
    #
    #     return reply_text

    def get_portfolio_description_str(self):

        data = prepare_coin_data(self.get_portfolio_data())
        last_updated = datetime.fromtimestamp(data["last_updated"]).strftime('%Y-%m-%d %H:%M:%S')

        coins = []
        for coin_symbol, data in data.items():
            if coin_symbol == "last_updated":
                continue
            coins.append(
                [coin_symbol.upper(), f"{data['price']}$ ({data['change_24h']})",
                 f"{data['holdings_price']}$ ({data['holdings_amount']})"])

        coin_data_table = tabulate(coins,
                                   headers=['Name', 'Price (change %)', 'Holdings (amount)'])
        reply_text = f"{coin_data_table}\n\nLast updated: {last_updated}"

        return reply_text
