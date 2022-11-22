import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, filters

from tracker.services.Cointracker import Cointracker
from tracker.services.Exception import CustomException
from tracker.utils.utils import get_config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
tracker = Cointracker()

DEVELOPER_CHAT_ID = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Get Portfolio", callback_data="get_portfolio"),
            InlineKeyboardButton("Update Portfolio", callback_data="update_portfolio")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    reply_text = str()
    if query.data == "get_portfolio":
        try:
            portfolio_price = tracker.get_portfolio_price()
            reply_text = f"Portfolio price: {portfolio_price:,} USD"
        except CustomException as e:
            reply_text = f"An error occurred.\nMessage: {e}"
            logger.error(e)

    await query.answer()
    await query.edit_message_text(text=reply_text)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    await query.answer()
    await query.edit_message_text(text=f"An error occured: {context.error}")


def start_bot() -> None:
    config = get_config().telegram
    application = Application.builder().token(config.api_key).build()
    application.add_handler(CommandHandler("start", start, filters=filters.User(username=config.users)))
    application.add_handler(CallbackQueryHandler(button))
    application.add_error_handler(error_handler)
    application.run_polling()

