import asyncio
import os
import random
import string

import fakeredis
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.custom.conversation import Conversation
from tracker.core.TelegramCointrackerBot import TelegramCointrackerBot

random_string = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
START_COMMAND = f"/{random_string}"


@pytest.fixture(autouse=True, scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
def bot(event_loop: asyncio.events.AbstractEventLoop):
    """
    Run bot for testing
    """
    bot = TelegramCointrackerBot(start_command_string=START_COMMAND[1:])
    bot.tracker.db.redis = fakeredis.FakeStrictRedis(version=6)
    stop_event = asyncio.Event()
    event_loop.create_task(bot.run_bot(stop_event=stop_event))
    yield
    stop_event.set()


@pytest_asyncio.fixture(scope="session")
async def telegram_client():
    """
    Connect to bot
    """
    load_dotenv()  # For local tests
    try:
        api_id = int(os.environ.get("TELEGRAM_APP_ID"))
        api_hash = os.environ.get("TELEGRAM_APP_HASH")
        session_str = os.environ.get("TELEGRAM_APP_SESSION")
    except TypeError:
        raise TypeError(".env file or environmental variables not found.")

    client = TelegramClient(
        StringSession(session_str), api_id, api_hash, sequential_updates=True
    )
    await client.connect()
    await client.get_me()
    await client.get_dialogs()
    yield client
    await client.disconnect()
    await client.disconnected


@pytest_asyncio.fixture(scope="session")
async def conv(telegram_client) -> Conversation:
    """
    Initialize conversation
    """
    async with telegram_client.conversation(
            os.environ.get("TELEGRAM_BOT_NAME"), timeout=10, max_messages=10000
    ) as conv:
        conv: Conversation
        yield conv
