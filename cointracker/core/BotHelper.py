import logging

from telegram import Update
from telegram.ext import ContextTypes

from cointracker.core.BotHelperReplyMarkups import BotHelperReplyMarkups
from cointracker.core.Cointracker import Cointracker
from cointracker.core.path_constants import PORTFOLIO_PRICE_UPDATE, START, COIN_ACTION_UPDATE, COIN_ACTION_ADD, \
    SET_COIN_AMOUNT, UPDATE_PORTFOLIO, UPDATE_MENU, END
from cointracker.services.Exception import CustomException
from cointracker.services.ExceptionCode import ExceptionCode
from cointracker.services.ExceptionMessage import ExceptionMessage


class BotHelper(BotHelperReplyMarkups):
    def __init__(self):
        super().__init__()
        self.tracker = Cointracker()
        self.logger = logging.getLogger('main')

    def get_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        self.tracker.db.set_user_prefix(update.callback_query.from_user.id)
        keyboard = self.get_keyboard([{"Update quotes": PORTFOLIO_PRICE_UPDATE, "Back": START}])
        if query.data == PORTFOLIO_PRICE_UPDATE:
            self.tracker.update_all_coins()
        try:
            price_data = self.tracker.get_portfolio_price()
            reply_text = "Portfolio price: {0:,} USD\n\n{1}".format(price_data["portfolio_price"],
                                                                                     self.tracker.get_portfolio_description_str())
        except CustomException as e:
            reply_text = f"An error occurred.\nMessage: {e}"
            keyboard = self.get_keyboard([{"Back": START}])
            self.logger.error(e)
        return reply_text, self.get_inline_keyboard_markup_from_keyboard(keyboard)

    def add_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_data = context.user_data
        user_data["prompt_type"] = COIN_ACTION_ADD

    def update_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        self.tracker.db.set_user_prefix(update.callback_query.from_user.id)
        try:
            coins = self.tracker.list_coins()
            if not coins:
                raise CustomException(code=ExceptionCode.INTERNAL_SERVER_ERROR,
                                      message=ExceptionMessage.COINTRACKER_DATA_PORTFOLIO_DATA_EMPTY)
            keyboard = self.get_coins_keyboard(coins)
            reply_text = "\n\nChoose coin"
        except CustomException as e:
            reply_text = f"An error occurred.\nMessage: {e}"
            keyboard = self.get_keyboard([{"Back": START}])
            self.logger.error(e)

        return reply_text, self.get_inline_keyboard_markup_from_keyboard(keyboard)

    def update_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        self.tracker.db.set_user_prefix(update.callback_query.from_user.id)
        user_data = context.user_data
        coin_symbol = query.data.split("update_portfolio_")[1]
        coin_amount = self.tracker.get_coin_data(coin_symbol)["amount"]
        user_data["prompt_type"] = COIN_ACTION_UPDATE
        user_data["coin_symbol"] = coin_symbol

        return {
            "coin_symbol": coin_symbol,
            "coin_amount": coin_amount
        }

    def process_user_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_data = context.user_data
        prompt_type = user_data["prompt_type"]
        if prompt_type == COIN_ACTION_UPDATE:
            keyboard, reply_text, coin_amount, _ = self.get_portfolio_update_metadata(
                coin_symbol=user_data["coin_symbol"],
                coin_amount=update.message.text)
            user_data["coin_action"] = COIN_ACTION_UPDATE
            user_data["coin_amount"] = float(coin_amount)
        elif prompt_type == COIN_ACTION_ADD:
            try:
                # Validating user input
                coin_symbol = update.message.text.split(" ")[0]
                coin_amount = update.message.text.split(" ")[1]
            except IndexError:
                coin_symbol = coin_amount = -1
            keyboard, reply_text, coin_amount, coin_symbol = self.get_portfolio_update_metadata(
                coin_symbol=coin_symbol,
                coin_amount=coin_amount)
            user_data["coin_action"] = COIN_ACTION_ADD
            user_data["coin_symbol"] = coin_symbol
            user_data["coin_amount"] = float(coin_amount)
        return reply_text, self.get_inline_keyboard_markup_from_keyboard(keyboard)

    def get_portfolio_update_metadata(self, coin_symbol, coin_amount):
        try:
            coin_amount = float(coin_amount)
            if coin_amount < 0 or not coin_symbol.isalnum():
                raise ValueError
            reply_text = f"Adding {coin_symbol.upper()} -> {coin_amount}"
            keyboard = self.get_keyboard([{"Yes": SET_COIN_AMOUNT, "No": UPDATE_PORTFOLIO}])
        except ValueError as e:
            reply_text = "Unable to set this amount, retry"
            coin_amount = -1
            coin_symbol = None
            keyboard = self.get_keyboard([{"Retry": UPDATE_MENU}])
        return keyboard, reply_text, coin_amount, coin_symbol

    def set_coin_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.tracker.db.set_user_prefix(update.callback_query.from_user.id)
        user_data = context.user_data
        coin_symbol, coin_amount, action = user_data["coin_symbol"], user_data["coin_amount"], user_data["coin_action"]
        if action == COIN_ACTION_ADD:
            self.tracker.add_coin(coin_symbol, coin_amount)
        elif action == COIN_ACTION_UPDATE:
            self.tracker.update_coin_amount(coin_symbol, coin_amount)
        reply_text = f"{coin_symbol.upper()} -> {coin_amount} updated!"
        keyboard = self.get_keyboard([{"Back": UPDATE_MENU, "Exit": END}])

        return reply_text, self.get_inline_keyboard_markup_from_keyboard(keyboard)
