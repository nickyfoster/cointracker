import logging
from logging.config import dictConfig

from services.TelegramCointrackerBot import TelegramCointrackerBot
from utils.logger_config import LOG_CONFIG
from utils.utils import get_hostname, fix_all_loggers

logger = logging.getLogger('main')

dictConfig(LOG_CONFIG)
fix_all_loggers()

logger.info(f"Initializing cointracker bot on {get_hostname()}")

bot = TelegramCointrackerBot()

bot.start_bot()
