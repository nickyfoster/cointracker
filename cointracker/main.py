import asyncio
import logging
from logging.config import dictConfig

from cointracker.core.Cointracker import Cointracker
from cointracker.core.TelegramCointrackerBot import TelegramCointrackerBot
from cointracker.services.PrometheusClient import PrometheusClient
from cointracker.utils.logger_config import LOG_CONFIG
from cointracker.utils.utils import get_hostname, get_config

logger = logging.getLogger('main')
dictConfig(LOG_CONFIG)
logger.info(f"Initializing cointracker bot on {get_hostname()}")

config = get_config()
# Preload initial portfolio data from config
if config.preload_data.do_preload:
    tracker = Cointracker()
    for coin, amount in config.preload_data.data.items():
        tracker.add_coin(coin, amount)
    del tracker


async def main():
    bot = TelegramCointrackerBot()
    prometheus = PrometheusClient()
    prometheus.run_server()

    stop_event = asyncio.Event()
    try:
        await asyncio.create_task(bot.run_bot(stop_event=stop_event))
    except KeyboardInterrupt:
        stop_event.set()
        # TODO exit gracefully


if __name__ == '__main__':
    asyncio.run(main())
