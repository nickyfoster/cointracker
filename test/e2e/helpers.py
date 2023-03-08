import re
from datetime import datetime
from time import sleep
from typing import Optional

from telethon.tl.custom import Conversation
from telethon.tl.custom.message import Message, MessageButton

from e2e.conftest import START_COMMAND


def wait(time=0.5):
    sleep(time)


# Simplifies the most frequent action - look for a button
# with a given text either to check that it exists or click it.
def get_button_with_text(message: Message, text: str, strict: bool = False) -> Optional[MessageButton]:
    """Return MessageButton from Message with text or None."""
    if message.buttons is None:
        return None

    for row in message.buttons:
        for button in row:
            if strict:
                is_match = text == button.text
            else:
                is_match = text in button.text
            if is_match:
                return button

    return None


def get_buttons(message: Message):
    res = []
    for button in message.buttons:
        if type(button) == list:
            for item in button:
                res.append(item.text)
    return res


async def go_to_add_coin_menu(conv: Conversation) -> Message:
    await conv.send_message(START_COMMAND)
    wait()
    reply: Message = await conv.get_response()
    await reply.buttons[0][1].click()  # -> Update portfolio
    wait()
    reply: Message = await conv.get_edit()
    await reply.buttons[0][0].click()  # -> Add coin
    wait()
    reply: Message = await conv.get_edit()
    return reply


async def go_to_show_portfolio_menu(conv: Conversation) -> Message:
    await conv.send_message(START_COMMAND)
    wait()
    reply: Message = await conv.get_response()
    await reply.buttons[0][0].click()  # -> Show portfolio
    wait()
    reply: Message = await conv.get_edit()
    return reply


async def go_to_update_portfolio_menu(conv: Conversation) -> Message:
    await conv.send_message(START_COMMAND)
    wait()
    reply: Message = await conv.get_response()
    await reply.buttons[0][1].click()  # -> Show portfolio
    wait()
    reply: Message = await conv.get_edit()
    return reply


async def go_to_update_coin_menu(conv: Conversation) -> Message:
    await conv.send_message(START_COMMAND)
    wait()
    reply: Message = await conv.get_response()
    await reply.buttons[0][1].click()  # -> Update portfolio
    wait()
    reply: Message = await conv.get_edit()
    await reply.buttons[0][1].click()  # -> Update coin
    wait()
    reply: Message = await conv.get_edit()
    return reply


def get_timestamp_from_portfolio_description_string(portfolio_description_str: str):
    try:
        found = re.search("(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})", portfolio_description_str)
        return datetime.strptime(portfolio_description_str[found.start():found.end()],
                                 '%Y-%m-%d %H:%M:%S')
    except AttributeError:
        return None
