import pytest
from telethon.tl.custom.conversation import Conversation
from telethon.tl.custom.message import Message

from e2e.env import START_COMMAND
from e2e.helpers import get_buttons, wait, go_to_add_coin_menu


@pytest.mark.asyncio
async def test_menu_main(conv: Conversation):
    await conv.send_message(START_COMMAND)
    reply: Message = await conv.get_response()
    assert "Please choose" in reply.text
    buttons = get_buttons(reply)
    assert buttons[0] == "Show Portfolio"
    assert buttons[1] == "Update Portfolio"


@pytest.mark.asyncio
async def test_empty_describe_portfolio(conv: Conversation):
    await conv.send_message(START_COMMAND)
    reply: Message = await conv.get_response()
    await reply.buttons[0][0].click()
    wait()
    reply: Message = await conv.get_edit()
    assert "portfolio_data_empty" in reply.text


@pytest.mark.asyncio
async def test_menu_update_main(conv: Conversation):
    await conv.send_message(START_COMMAND)
    reply: Message = await conv.get_response()
    await reply.buttons[0][1].click()
    wait()
    reply: Message = await conv.get_edit()
    buttons = get_buttons(reply)
    assert buttons[0] == "Add new coin"
    assert buttons[1] == "Update portfolio"
    assert buttons[3] == "Back"


@pytest.mark.asyncio
async def test_empty_update_portfolio(conv: Conversation):
    await conv.send_message(START_COMMAND)
    reply: Message = await conv.get_response()
    await reply.buttons[0][1].click()
    wait()
    reply: Message = await conv.get_edit()
    await reply.buttons[0][1].click()
    wait()
    reply: Message = await conv.get_edit()
    assert "portfolio_data_empty" in reply.text


@pytest.mark.asyncio
async def test_menu_add_coin_add_invalid_coin(conv: Conversation):
    add_coin_menu_text: Message = await go_to_add_coin_menu(conv)
    assert "Enter coin symbol and amount" in add_coin_menu_text.text
    await conv.send_message("BTC INVALID>$")
    reply: Message = await conv.get_response()
    assert "Unable to set this amount" in reply.text
    await reply.buttons[0][0].click()  # -> Back
    wait()
    reply: Message = await conv.get_edit()
    assert "Please choose" in reply.text


@pytest.mark.asyncio
async def test_menu_add_coin_valid_coin(conv: Conversation):
    add_coin_menu_text: Message = await go_to_add_coin_menu(conv)
    assert "Enter coin symbol and amount" in add_coin_menu_text.text
    await conv.send_message("BTC 10")
    reply: Message = await conv.get_response()
    assert "Adding BTC -> 10.0" in reply.text
    await reply.buttons[0][0].click()  # -> Yes
    reply: Message = await conv.get_edit()
    assert "BTC -> 10.0 updated!" in reply.text

# TODO tests:
#   - Return btns
#   - Redis clean before & after
#   - Coin update
#   - Portfolio change & update
