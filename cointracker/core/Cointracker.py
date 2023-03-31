import json
import logging
import time
from datetime import datetime

from cointracker.core.CoinmarketcapAPI import CoinmarketcapAPI
from cointracker.services.Exception import CustomException
from cointracker.services.ExceptionCode import ExceptionCode
from cointracker.services.ExceptionMessage import ExceptionMessage
from cointracker.utils.utils import get_db_connector, update_nested_dict, prepare_coin_data, CoinFromPortfolio, \
    get_config


class Cointracker:
    def __init__(self):
        self.db = get_db_connector()
        self.api = CoinmarketcapAPI()
        self.config = get_config()
        self.logger = logging.getLogger('main')

    def set_coin_data(self, coin_symbol: str, data: dict):
        data["last_updated"] = time.time()
        self.db.set(key=coin_symbol, data=json.dumps(data))

    def get_coin_data(self, coin_symbol: str):
        if self.db.exists(coin_symbol):
            return json.loads(self.db.get(coin_symbol))
        else:
            return dict()

    def update_coins_data(self, coins: list):
        api_data = self.api.get_currency_quotes_latest(coins)
        if api_data["status"]["error_code"] != 0:
            raise CustomException(code=ExceptionCode.INTERNAL_SERVER_ERROR,
                                  message=ExceptionMessage.COINTRACKER_DATA_PORTFOLIO_DATA_INVALID)
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
        self.db.delete_key(coin_symbol)

    def list_coins(self):
        coins = self.db.list_coin_keys()
        res = list()
        for coin in coins:
            res.append(coin.split('coin/')[1])
        return res

    def fill_db(self, coins_raw_data: dict):
        for coin_name, coin_amount in coins_raw_data.items():
            self.update_coin_amount(coin_name, float(coin_amount))

    def get_portfolio_data(self):
        coins_symbols = self.list_coins()
        if not coins_symbols:
            raise CustomException(code=ExceptionCode.INTERNAL_SERVER_ERROR,
                                  message=ExceptionMessage.COINTRACKER_DATA_PORTFOLIO_DATA_EMPTY)
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

        if not portfolio_data:
            return None

        for coin_symbol, coin_data in portfolio_data.items():
            last_update_time += float(coin_data["last_updated"])
            try:
                portfolio_price += float(coin_data['quote']['USD']['price']) * float(coin_data['amount'])
            except KeyError:
                self.logger.error(f"Invalid coin detected: {coin_symbol.upper()}. Removing from portfolio.")
                self.delete_coin(coin_symbol)
        result["last_updated"] = last_update_time / len(portfolio_data)
        result["portfolio_price"] = round(portfolio_price, 2)
        return result

    def get_portfolio_description_str(self):
        data = prepare_coin_data(self.get_portfolio_data())
        last_updated = datetime.fromtimestamp(data["last_updated"]).strftime('%Y-%m-%d %H:%M:%S')

        coins = []
        for coin_symbol, data in data.items():
            if coin_symbol == "last_updated":
                continue
            coins.append(CoinFromPortfolio(symbol=coin_symbol.upper(),
                                           name=data['name'],
                                           price=data['price'],
                                           change_24h=data['change_24h'],
                                           holdings_price=data['holdings_price'],
                                           holdings_amount=data['holdings_amount']))

        coins = sorted(coins, key=lambda x: float(x.holdings_price))
        coins_text = ""
        for coin in coins:
            coins_text += f"{coin.__str__()}\n\n"

        reply_text = f"{coins_text}\nLast updated: {last_updated}"
        return reply_text
