import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, filters

from services.Cointracker import Cointracker
from utils.utils import get_config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
tracker = Cointracker()


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
    if query.data == "get_portfolio":
        portfolio_price = tracker.get_portfolio_price()

    await query.answer()
    await query.edit_message_text(text=f"Portfolio price: {portfolio_price:,} USD")


def main() -> None:
    config = get_config().telegram
    application = Application.builder().token(config.api_key).build()
    application.add_handler(CommandHandler("start", start, filters=filters.User(username=config.users)))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == "__main__":
    main()
