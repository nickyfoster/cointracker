import logging

from telegram import __version__ as TG_VER
from telegram.ext import filters, MessageHandler

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
from tracker.services.Cointracker import Cointracker
from tracker.services.Exception import CustomException
from tracker.utils.utils import get_config


class TelegramCointrackerBot:
    def __init__(self):
        self.START = "start"
        self.END = "end"
        self.GET_PORTFOLIO = "get_portfolio"
        self.UPDATE_PORTFOLIO = "update_portfolio"
        self.PORTFOLIO_PRICE = "portfolio_price"
        self.PORTFOLIO_PRICE_UPDATE = "portfolio_price_update"
        self.PORTFOLIO_DESCRIPTION = "portfolio_description"
        self.SET_COIN_AMOUNT = "set_coin_amount"
        self.INLINE_BUTTON_ROUTES = "inline_button_routes"
        self.USER_INPUT_ROUTES = "user_input_routes"

        self.logger = logging.getLogger(__name__)
        self.tracker = Cointracker()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        user = update.message.from_user
        self.logger.info(
            f"User {user.first_name} {user.last_name} ({user.username}|{user.id}) started the conversation.")
        keyboard = [
            [
                InlineKeyboardButton("Show Portfolio", callback_data=self.GET_PORTFOLIO),
                InlineKeyboardButton("Update Portfolio", callback_data=self.UPDATE_PORTFOLIO)
            ]
        ]

        await update.message.reply_text("Please choose", reply_markup=InlineKeyboardMarkup(keyboard))
        return self.INLINE_BUTTON_ROUTES

    async def start_over(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        query = update.callback_query
        await query.answer()
        keyboard = [
            [
                InlineKeyboardButton("Show Portfolio", callback_data=self.GET_PORTFOLIO),
                InlineKeyboardButton("Update Portfolio", callback_data=self.UPDATE_PORTFOLIO)
            ]
        ]
        await query.edit_message_text(text="Please choose", reply_markup=InlineKeyboardMarkup(keyboard))
        return self.INLINE_BUTTON_ROUTES

    async def get_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        query = update.callback_query
        await query.answer()
        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data=self.PORTFOLIO_PRICE_UPDATE),
                InlineKeyboardButton("Back", callback_data=self.START),
            ]
        ]
        if query.data == self.PORTFOLIO_PRICE_UPDATE:
            self.tracker.update_all_coins()

        try:
            data = self.tracker.get_portfolio_price()
            portfolio_price = data["portfolio_price"]
            portfolio_data = self.tracker.get_portfolio_description_str()

            reply_text = "Portfolio price: {0:,} USD\n\n{1}".format(portfolio_price, portfolio_data)

        except CustomException as e:
            reply_text = f"An error occurred.\nMessage: {e}"
            self.logger.error(e)

        reply_text += "\n\nUpdate price?"
        await query.edit_message_text(
            text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return self.INLINE_BUTTON_ROUTES

    async def update_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        query = update.callback_query
        await query.answer()
        coins = self.tracker.list_coins()
        keyboard = [[], [], [], [InlineKeyboardButton("Back", callback_data=self.START)]]
        cnt = 0
        for coin in coins:
            coin_symbol = str(coin)
            keyboard[cnt % 3].append(
                InlineKeyboardButton(coin_symbol.upper(),
                                     callback_data=f"{self.UPDATE_PORTFOLIO}_{coin_symbol.lower()}"))
            cnt += 1

        reply_text = "\n\nChoose coin"
        await query.edit_message_text(
            text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return self.INLINE_BUTTON_ROUTES

    async def update_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        query = update.callback_query
        user_data = context.user_data

        await query.answer()
        coin_symbol = query.data.split("update_portfolio_")[1]
        user_data["coin_symbol"] = coin_symbol

        coin_amount = self.tracker.get_coin_data(coin_symbol)["amount"]
        reply_text = f"{coin_symbol.upper()} amount is {coin_amount}\nEnter new amount:"
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=reply_text)

        return self.USER_INPUT_ROUTES

    async def prompt_coin_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Save input for feature and return to feature selection."""
        user_data = context.user_data
        coin_symbol = user_data["coin_symbol"]

        try:
            coin_amount = float(update.message.text)
            if coin_amount < 0:
                raise ValueError
            reply_text = f"Setting {coin_symbol.upper()} -> {coin_amount}"
            keyboard = [
                [
                    InlineKeyboardButton("Yes", callback_data=self.SET_COIN_AMOUNT),
                    InlineKeyboardButton("No", callback_data=self.UPDATE_PORTFOLIO),
                ]
            ]
        except ValueError as e:
            reply_text = "Unable to set this amount, retry"
            coin_amount = -1
            keyboard = [
                [
                    InlineKeyboardButton("Retry", callback_data=self.UPDATE_PORTFOLIO)
                ]
            ]
        user_data["coin_amount"] = float(coin_amount)
        await update.message.reply_text(text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))

        return self.INLINE_BUTTON_ROUTES

    async def set_coin_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        user_data = context.user_data

        coin_symbol = user_data["coin_symbol"]
        coin_amount = user_data["coin_amount"]
        self.tracker.update_coin_amount(coin_symbol, coin_amount)
        reply_text = f"{coin_symbol.upper()} -> {coin_amount} updated!"

        keyboard = [
            [
                InlineKeyboardButton("Back", callback_data=self.UPDATE_PORTFOLIO),
                InlineKeyboardButton("Exit", callback_data=self.END),
            ]
        ]

        await query.edit_message_text(text=reply_text, reply_markup=InlineKeyboardMarkup(keyboard))

        return self.INLINE_BUTTON_ROUTES

    async def end(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="See ya!")
        return ConversationHandler.END

    def start_bot(self) -> None:
        config = get_config().telegram
        application = Application.builder().token(config.api_key).build()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                self.INLINE_BUTTON_ROUTES: [
                    CallbackQueryHandler(self.get_portfolio, pattern="^" + self.GET_PORTFOLIO + "$"),
                    CallbackQueryHandler(self.update_portfolio, pattern="^" + self.UPDATE_PORTFOLIO + "$"),
                    CallbackQueryHandler(self.update_coin, pattern=f"^{self.UPDATE_PORTFOLIO}_[a-z]+$"),
                    CallbackQueryHandler(self.get_portfolio,
                                         pattern=f"^{self.PORTFOLIO_PRICE}|{self.PORTFOLIO_PRICE_UPDATE}$"),
                    CallbackQueryHandler(self.set_coin_amount, pattern="^" + self.SET_COIN_AMOUNT + "$"),
                    CallbackQueryHandler(self.start_over, pattern="^" + self.START + "$"),
                    CallbackQueryHandler(self.end, pattern="^" + self.END + "$")
                ],
                self.USER_INPUT_ROUTES: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.prompt_coin_amount)
                ]
            },
            fallbacks=[CommandHandler("start", self.start)]
        )

        application.add_handler(conv_handler)
        # application.add_error_handler(self.error_handler)
        application.run_polling()

# TODO add filter
# filters.User(username=config.users)
