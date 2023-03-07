import asyncio
import logging
from logging.config import dictConfig

from tracker.core.Cointracker import Cointracker
from tracker.core.TelegramCointrackerBot import TelegramCointrackerBot
from utils.logger_config import LOG_CONFIG
from utils.utils import get_hostname, get_config

logger = logging.getLogger('main')

dictConfig(LOG_CONFIG)
# fix_all_loggers()

logger.info(f"Initializing cointracker bot on {get_hostname()}")

config = get_config()
if config.preload_data.do_preload:
    tracker = Cointracker()
    for coin, amount in config.preload_data.data.items():
        tracker.add_coin(coin, amount)


async def main():
    bot = TelegramCointrackerBot()
    stop_event = asyncio.Event()
    try:
        await asyncio.create_task(bot.run_bot(stop_event=stop_event))
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == '__main__':
    asyncio.run(main())
