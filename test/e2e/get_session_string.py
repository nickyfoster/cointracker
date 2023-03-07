from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()
api_id = int(os.environ.get("TELEGRAM_APP_ID"))
api_hash = os.environ.get("TELEGRAM_APP_HASH")

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("Session string:", client.session.save())
