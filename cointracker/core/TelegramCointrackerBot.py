import logging
import os
import time
from asyncio import Event
from typing import Optional

from telegram import __version__ as TG_VER
from telegram.ext import filters, MessageHandler

from cointracker.services.ExceptionCode import ExceptionCode
from cointracker.services.ExceptionMessage import ExceptionMessage

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)
from cointracker.core.Cointracker import Cointracker
from cointracker.services.Exception import CustomException
from cointracker.utils.utils import get_config, run_thread


class TelegramCointrackerBot:
    START = "start"
    END = "end"
    GET_PORTFOLIO = "get_portfolio"
    UPDATE_PORTFOLIO = "update_portfolio"
    UPDATE_MENU = "update_menu"
    ADD_COIN = "add_coin"
    PORTFOLIO_PRICE = "portfolio_price"
    PORTFOLIO_PRICE_UPDATE = "portfolio_price_update"
    PORTFOLIO_DESCRIPTION = "portfolio_description"
    SET_COIN_AMOUNT = "set_coin_amount"
    INLINE_BUTTON_ROUTES = "inline_button_routes"
    USER_INPUT_ROUTES = "user_input_routes"
    COIN_ACTION_UPDATE = "coin_action_update"
    COIN_ACTION_ADD = "coin_action_add"

    def __init__(self, db_class: str = "Redis", start_command_string: str = "start"):
        self.start_command_string = start_command_string
        self.db_class = db_class
        self.logger = logging.getLogger(__name__)
        self.tracker = Cointracker()
        self.config = get_config()
        self.application = self.init_bot(self.config.telegram)

    def init_bot(self, config):
        api_key = os.environ.get("TELEGRAM_BOT_API_KEY")
        if not api_key:
            api_key = config.api_key
        application = Application.builder().token(api_key).build()
        application.add_handler(self.get_conv_handler())

        return application

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        user = update.message.from_user
        self.tracker.db.set_user_prefix(user.id)
        if self.config.db.migrate:
            self.tracker.db.migrate()
        self.logger.info(
            f"User {user.first_name} {user.last_name} ({user.username}|{user.id}) started the conversation.")
        await update.message.reply_text("Please choose", reply_markup=InlineKeyboardMarkup(self.get_keyboard(
            [{"Show Portfolio": self.GET_PORTFOLIO, "Update Portfolio": self.UPDATE_MENU}])))
        return self.INLINE_BUTTON_ROUTES

    async def start_over(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        query = update.callback_query
        await query.answer()
        keyboard = self.get_keyboard(
            [{"Show Portfolio": self.GET_PORTFOLIO, "Update Portfolio": self.UPDATE_MENU}])
        await query.edit_message_text(text="Please choose", reply_markup=InlineKeyboardMarkup(keyboard))
        return self.INLINE_BUTTON_ROUTES

    async def get_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        self.tracker.db.set_user_prefix(update.callback_query.from_user.id)
        query = update.callback_query

        await query.answer()

        keyboard = self.get_keyboard([{"Yes": self.PORTFOLIO_PRICE_UPDATE, "Back": self.START}])
        if query.data == self.PORTFOLIO_PRICE_UPDATE:
            self.tracker.update_all_coins()
        try:
            data = self.tracker.get_portfolio_price()
            if not data:
                raise CustomException(code=ExceptionCode.INTERNAL_SERVER_ERROR,
                                      message=ExceptionMessage.COINTRACKER_DATA_PORTFOLIO_DATA_EMPTY)

            reply_text = "Portfolio price: {0:,} USD\n\n{1}\n\nUpdate price?".format(data["portfolio_price"],
                                                                                     self.tracker.get_portfolio_description_str())
        except CustomException as e:
            reply_text = f"An error occurred.\nMessage: {e}"
            keyboard = self.get_keyboard([{"Back": self.START}])
            self.logger.error(e)
        await query.edit_message_text(
            text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return self.INLINE_BUTTON_ROUTES

    async def update_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        keyboard = self.get_keyboard(
            [{"Add coin": self.ADD_COIN, "Update coin": self.UPDATE_PORTFOLIO}, {"Back": self.START}])
        await query.edit_message_text(text="Please choose", reply_markup=InlineKeyboardMarkup(keyboard))
        return self.INLINE_BUTTON_ROUTES

    async def add_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        query = update.callback_query
        user_data = context.user_data
        user_data["prompt_type"] = self.COIN_ACTION_ADD
        await query.answer()
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text="Enter coin symbol and amount in the following format:\n\nBTC 1.5")
        return self.USER_INPUT_ROUTES

    async def update_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        self.tracker.db.set_user_prefix(update.callback_query.from_user.id)
        query = update.callback_query
        await query.answer()
        try:
            coins = self.tracker.list_coins()
            if not coins:
                raise CustomException(code=ExceptionCode.INTERNAL_SERVER_ERROR,
                                      message=ExceptionMessage.COINTRACKER_DATA_PORTFOLIO_DATA_EMPTY)
            keyboard = self.get_coins_keyboard(coins)
            reply_text = "\n\nChoose coin"
        except CustomException as e:
            reply_text = f"An error occurred.\nMessage: {e}"
            keyboard = self.get_keyboard([{"Back": self.START}])
            self.logger.error(e)
        await query.edit_message_text(
            text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return self.INLINE_BUTTON_ROUTES

    async def update_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        self.tracker.db.set_user_prefix(update.callback_query.from_user.id)
        query = update.callback_query
        user_data = context.user_data
        await query.answer()
        coin_symbol = query.data.split("update_portfolio_")[1]
        user_data["prompt_type"] = self.COIN_ACTION_UPDATE
        user_data["coin_symbol"] = coin_symbol
        coin_amount = self.tracker.get_coin_data(coin_symbol)["amount"]
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=f"{coin_symbol.upper()} amount is {coin_amount}\nEnter new amount:")
        return self.USER_INPUT_ROUTES

    async def process_user_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        user_data = context.user_data
        prompt_type = user_data["prompt_type"]
        if prompt_type == self.COIN_ACTION_UPDATE:
            keyboard, reply_text, coin_amount, _ = self.get_portfolio_update_metadata(
                coin_symbol=user_data["coin_symbol"],
                coin_amount=update.message.text)
            user_data["coin_action"] = self.COIN_ACTION_UPDATE
            user_data["coin_amount"] = float(coin_amount)
        elif prompt_type == self.COIN_ACTION_ADD:
            try:
                # Validating user input
                coin_symbol = update.message.text.split(" ")[0]
                coin_amount = update.message.text.split(" ")[1]
            except IndexError:
                # TODO rewrite this bs
                coin_symbol = coin_amount = -1
            keyboard, reply_text, coin_amount, coin_symbol = self.get_portfolio_update_metadata(
                coin_symbol=coin_symbol,
                coin_amount=coin_amount)
            user_data["coin_action"] = self.COIN_ACTION_ADD
            user_data["coin_symbol"] = coin_symbol
            user_data["coin_amount"] = float(coin_amount)
        await update.message.reply_text(text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return self.INLINE_BUTTON_ROUTES

    async def set_coin_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.tracker.db.set_user_prefix(update.callback_query.from_user.id)
        query = update.callback_query
        await query.answer()
        user_data = context.user_data
        coin_symbol, coin_amount, action = user_data["coin_symbol"], user_data["coin_amount"], user_data["coin_action"]
        if action == self.COIN_ACTION_ADD:
            self.tracker.add_coin(coin_symbol, coin_amount)
        elif action == self.COIN_ACTION_UPDATE:
            self.tracker.update_coin_amount(coin_symbol, coin_amount)
        reply_text = f"{coin_symbol.upper()} -> {coin_amount} updated!"
        keyboard = self.get_keyboard([{"Back": self.UPDATE_MENU, "Exit": self.END}])
        await query.edit_message_text(text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
        return self.INLINE_BUTTON_ROUTES

    async def end(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="See ya!")
        return ConversationHandler.END

    def get_portfolio_update_metadata(self, coin_symbol, coin_amount):
        # TODO add to unit test
        try:
            coin_amount = float(coin_amount)
            if coin_amount < 0 or not coin_symbol.isalnum():
                raise ValueError
            reply_text = f"Adding {coin_symbol.upper()} -> {coin_amount}"
            keyboard = self.get_keyboard([{"Yes": self.SET_COIN_AMOUNT, "No": self.UPDATE_PORTFOLIO}])
        except ValueError as e:
            reply_text = "Unable to set this amount, retry"
            coin_amount = -1
            coin_symbol = None
            keyboard = self.get_keyboard([{"Retry": self.UPDATE_MENU}])
        return keyboard, reply_text, coin_amount, coin_symbol

    @staticmethod
    def run_liveness_probe():
        while True:
            with open("/tmp/liveness-probe", "w") as f:
                f.write(str(int(time.time())))
            time.sleep(5)

    @staticmethod
    def get_keyboard(keyboard_layout):
        """
        keyboard_data = [
                {"Start": callback_data, "End": callback_data},
                {"Back": callback_data}
        ]
        """
        keyboard = [[] for _ in range(len(keyboard_layout))]

        for index, row in enumerate(keyboard_layout):
            for name, callback_data in row.items():
                keyboard[index].append(InlineKeyboardButton(name, callback_data=callback_data))
        return keyboard

    def get_coins_keyboard(self, coins, n_rows: int = 3):
        keyboard = [[] for _ in range(n_rows)]
        keyboard.append([InlineKeyboardButton("Back", callback_data=self.START)])
        cnt = 0
        for coin in coins:
            coin_symbol = str(coin)
            keyboard[cnt % n_rows].append(
                InlineKeyboardButton(coin_symbol.upper(),
                                     callback_data=f"{self.UPDATE_PORTFOLIO}_{coin_symbol.lower()}"))
            cnt += 1
        return keyboard

    def get_conv_handler(self):
        return ConversationHandler(
            entry_points=[CommandHandler(self.start_command_string, self.start)],
            states={
                self.INLINE_BUTTON_ROUTES: [
                    CallbackQueryHandler(self.get_portfolio, pattern="^" + self.GET_PORTFOLIO + "$"),
                    CallbackQueryHandler(self.update_menu, pattern="^" + self.UPDATE_MENU + "$"),
                    CallbackQueryHandler(self.add_coin, pattern="^" + self.ADD_COIN + "$"),
                    CallbackQueryHandler(self.update_portfolio, pattern="^" + self.UPDATE_PORTFOLIO + "$"),
                    CallbackQueryHandler(self.update_coin, pattern=f"^{self.UPDATE_PORTFOLIO}_[a-z]+$"),
                    CallbackQueryHandler(self.get_portfolio,
                                         pattern=f"^{self.PORTFOLIO_PRICE}|{self.PORTFOLIO_PRICE_UPDATE}$"),
                    CallbackQueryHandler(self.set_coin_amount, pattern="^" + self.SET_COIN_AMOUNT + "$"),
                    CallbackQueryHandler(self.start_over, pattern="^" + self.START + "$"),
                    CallbackQueryHandler(self.end, pattern="^" + self.END + "$")
                ],
                self.USER_INPUT_ROUTES: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.process_user_prompt)
                ]
            },
            fallbacks=[CommandHandler(self.start_command_string, self.start)]
        )

    async def run_bot(self, stop_event: Optional[Event] = None):
        run_thread(self.run_liveness_probe)

        async with self.application:
            await self.application.start()
            await self.application.updater.start_polling()
            self.logger.info("Started cointracker bot")
            await stop_event.wait()

            await self.application.updater.stop()
            await self.application.stop()
