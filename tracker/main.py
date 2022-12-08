import logging
from logging.config import dictConfig

from tracker.services.Cointracker import Cointracker
from tracker.services.TelegramCointrackerBot import TelegramCointrackerBot
from utils.logger_config import LOG_CONFIG
from utils.utils import get_hostname, fix_all_loggers, get_config

logger = logging.getLogger('main')

dictConfig(LOG_CONFIG)
fix_all_loggers()

logger.info(f"Initializing cointracker bot on {get_hostname()}")
config = get_config()
if config.preload_data.do_preload:
    tracker = Cointracker()
    for coin, amount in config.preload_data.data.items():
        tracker.add_coin(coin, amount)

bot = TelegramCointrackerBot()

bot.start_bot()
