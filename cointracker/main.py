import asyncio
import logging
from logging.config import dictConfig

from cointracker.core.TelegramCointrackerBot import TelegramCointrackerBot
from cointracker.services.PrometheusClient import PrometheusClient
from cointracker.utils.logger_config import LOG_CONFIG
from cointracker.utils.utils import get_hostname

logger = logging.getLogger('main')
dictConfig(LOG_CONFIG)
logger.info(f"Initializing cointracker bot on {get_hostname()}")


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
