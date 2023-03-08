import logging
import time
from asyncio import Event
from typing import Optional

from telegram import __version__ as TG_VER
from telegram.ext import filters, MessageHandler

from cointracker.core.BotHelper import BotHelper
from cointracker.core.BotHelperReplyMarkups import BotHelperReplyMarkups
from cointracker.core.path_constants import INLINE_BUTTON_ROUTES, USER_INPUT_ROUTES, \
    END, UPDATE_MENU, GET_PORTFOLIO, UPDATE_PORTFOLIO, ADD_COIN, PORTFOLIO_PRICE, PORTFOLIO_PRICE_UPDATE, \
    SET_COIN_AMOUNT, START

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
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)
from cointracker.core.Cointracker import Cointracker
from cointracker.utils.utils import run_thread, get_api_key, get_user_obj_from_update


class TelegramCointrackerBot:

    def __init__(self, start_command_string: str = "start"):
        self.start_command_string = start_command_string
        self.logger = logging.getLogger(__name__)
        self.helper = BotHelper()
        self.tracker = Cointracker()
        self.reply_markups = BotHelperReplyMarkups()
        self.application = self.init_bot()

    def init_bot(self):
        api_key = get_api_key(api_name="Telegram")
        self.logger.debug("Building bot backend...")
        application = Application.builder().token(api_key).build()
        application.add_handler(self.get_conv_handler())
        self.logger.debug("Done building bot backend!")
        return application

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        user = get_user_obj_from_update(update)
        self.logger.info(
            f"User {user.first_name} {user.last_name} ({user.username}|{user.id}) started the conversation.")
        await update.message.reply_text("Please choose", reply_markup=self.helper.get_start_reply_markup())
        return INLINE_BUTTON_ROUTES

    async def start_over(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        user = get_user_obj_from_update(update)
        self.logger.debug(f"User: {user.full_name} in /start_over")
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text="Please choose",
                                                      reply_markup=self.helper.get_start_reply_markup())
        return INLINE_BUTTON_ROUTES

    async def get_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        user = get_user_obj_from_update(update)
        self.logger.debug(f"User: {user.full_name} in /get_portfolio")
        await update.callback_query.answer()
        reply_text, reply_markup = self.helper.get_portfolio(update, context)
        await update.callback_query.edit_message_text(text=reply_text, reply_markup=reply_markup)
        return INLINE_BUTTON_ROUTES

    async def update_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = get_user_obj_from_update(update)
        self.logger.debug(f"User: {user.full_name} in /update_menu")
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="Please choose", reply_markup=self.helper.get_update_menu_reply_markup())
        return INLINE_BUTTON_ROUTES

    async def add_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        user = get_user_obj_from_update(update)
        self.logger.debug(f"User: {user.full_name} in /add_coin")
        self.helper.add_coin(update, context)
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text="Enter coin symbol and amount in the following format: <COIN_NAME> <COIN_AMOUNT>\n\nExample: BTC 1.5")
        return USER_INPUT_ROUTES

    async def update_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        user = get_user_obj_from_update(update)
        self.logger.debug(f"User: {user.full_name} in /update_portfolio")
        await update.callback_query.answer()
        reply_text, reply_markup = self.helper.update_portfolio(update, context)
        await update.callback_query.edit_message_text(text=reply_text, reply_markup=reply_markup)
        return INLINE_BUTTON_ROUTES

    async def update_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        user = get_user_obj_from_update(update)
        self.logger.debug(f"User: {user.full_name} in /update_coin")
        await update.callback_query.answer()
        coin_data = self.helper.update_coin(update, context)
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=f"{coin_data['coin_symbol'].upper()} amount is {coin_data['coin_amount']}\nEnter new amount:")
        return USER_INPUT_ROUTES

    async def process_user_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        user = get_user_obj_from_update(update)
        self.logger.debug(f"User: {user.full_name} in /process_user_prompt")
        reply_text, reply_markup = self.helper.process_user_prompt(update, context)
        await update.message.reply_text(text=reply_text, reply_markup=reply_markup)
        return INLINE_BUTTON_ROUTES

    async def set_coin_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = get_user_obj_from_update(update)
        self.logger.debug(f"User: {user.full_name} in /set_coin_amount")
        await update.callback_query.answer()
        reply_text, reply_markup = self.helper.set_coin_amount(update, context)
        await update.callback_query.edit_message_text(text=reply_text, reply_markup=reply_markup)
        return INLINE_BUTTON_ROUTES

    async def end(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = get_user_obj_from_update(update)
        self.logger.debug(f"User: {user.full_name} in /end")
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text="See ya!")
        return END

    @staticmethod
    def run_liveness_probe():
        while True:
            with open("/tmp/liveness-probe", "w") as f:
                f.write(str(int(time.time())))
            time.sleep(5)

    def get_conv_handler(self):
        return ConversationHandler(
            entry_points=[CommandHandler(self.start_command_string, self.start)],
            states={
                INLINE_BUTTON_ROUTES: [
                    CallbackQueryHandler(self.get_portfolio, pattern="^" + GET_PORTFOLIO + "$"),
                    CallbackQueryHandler(self.update_menu, pattern="^" + UPDATE_MENU + "$"),
                    CallbackQueryHandler(self.add_coin, pattern="^" + ADD_COIN + "$"),
                    CallbackQueryHandler(self.update_portfolio, pattern="^" + UPDATE_PORTFOLIO + "$"),
                    CallbackQueryHandler(self.update_coin, pattern=f"^{UPDATE_PORTFOLIO}_[a-z]+$"),
                    CallbackQueryHandler(self.get_portfolio,
                                         pattern=f"^{PORTFOLIO_PRICE}|{PORTFOLIO_PRICE_UPDATE}$"),
                    CallbackQueryHandler(self.set_coin_amount, pattern="^" + SET_COIN_AMOUNT + "$"),
                    CallbackQueryHandler(self.start_over, pattern="^" + START + "$"),
                    CallbackQueryHandler(self.end, pattern="^" + END + "$")
                ],
                USER_INPUT_ROUTES: [
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
