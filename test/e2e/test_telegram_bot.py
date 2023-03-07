import pytest
from telethon.tl.custom.conversation import Conversation
from telethon.tl.custom.message import Message

from e2e.conftest import START_COMMAND
from e2e.helpers import get_buttons, wait, go_to_add_coin_menu, go_to_show_portfolio_menu, go_to_update_portfolio_menu, \
    get_timestamp_from_portfolio_description_string, go_to_update_coin_menu

test_data = {
    "coin_name": "BTC",
    "coin_amount": 10,
    "coin_update_amount": 11,
    "invalid_coin_name": "B1T&a$$"
}


@pytest.mark.asyncio
async def test_001_open_main_menu(conv: Conversation):
    await conv.send_message(START_COMMAND)
    reply: Message = await conv.get_response()
    assert "Please choose" in reply.text
    buttons = get_buttons(reply)
    assert buttons[0] == "Show Portfolio"
    assert buttons[1] == "Update Portfolio"


@pytest.mark.asyncio
async def test_002_open_empty_portfolio(conv: Conversation):
    reply: Message = await go_to_show_portfolio_menu(conv)
    assert "portfolio_data_empty" in reply.text


@pytest.mark.asyncio
async def test_003_open_update_portfolio_menu(conv: Conversation):
    reply: Message = await go_to_update_portfolio_menu(conv)
    buttons = get_buttons(reply)
    assert buttons[0] == "Add coin"
    assert buttons[1] == "Update coin"
    assert buttons[2] == "Back"


@pytest.mark.asyncio
async def test_004_update_empty_portfolio(conv: Conversation):
    reply: Message = await go_to_update_portfolio_menu(conv)
    await reply.buttons[0][1].click()
    wait()
    reply: Message = await conv.get_edit()
    assert "portfolio_data_empty" in reply.text


@pytest.mark.asyncio
async def test_005_add_invalid_coin(conv: Conversation):
    invalid_coin_name = test_data["invalid_coin_name"]
    add_coin_menu_text: Message = await go_to_add_coin_menu(conv)
    assert "Enter coin symbol and amount" in add_coin_menu_text.text
    await conv.send_message(invalid_coin_name)
    reply: Message = await conv.get_response()
    assert "Unable to set this amount" in reply.text
    await reply.buttons[0][0].click()
    wait()
    reply: Message = await conv.get_edit()
    assert "Please choose" in reply.text


@pytest.mark.asyncio
async def test_006_add_coin_valid_coin(conv: Conversation):
    coin_name = test_data['coin_name']
    coin_amount = test_data['coin_amount']

    add_coin_menu_text: Message = await go_to_add_coin_menu(conv)
    assert "Enter coin symbol and amount" in add_coin_menu_text.text
    await conv.send_message(f"{coin_name} {coin_amount}")
    reply: Message = await conv.get_response()
    assert reply.text == f"Adding {coin_name} -> {float(coin_amount)}"
    await reply.buttons[0][0].click()
    wait()
    reply: Message = await conv.get_edit()
    assert reply.text == f"{coin_name} -> {float(coin_amount)} updated!"


@pytest.mark.asyncio
async def test_007_show_portfolio_with_new_coin(conv: Conversation):
    coin_name = test_data['coin_name']
    reply: Message = await go_to_show_portfolio_menu(conv)
    assert coin_name in reply.text


@pytest.mark.asyncio
async def test_008_show_updated_portfolio(conv: Conversation):
    reply: Message = await go_to_show_portfolio_menu(conv)
    assert "Update price?" in reply.text
    time_before_update = get_timestamp_from_portfolio_description_string(reply.text)
    await reply.buttons[0][0].click()
    wait(time=1.1)
    reply: Message = await conv.get_edit()
    time_after_update = get_timestamp_from_portfolio_description_string(reply.text)
    assert time_after_update > time_before_update


@pytest.mark.asyncio
async def test_009_update_coin(conv: Conversation):
    coin_name = test_data['coin_name']
    coin_amount = test_data['coin_amount']
    coin_update_amount = test_data['coin_update_amount']
    reply: Message = await go_to_update_coin_menu(conv)
    wait()
    assert "Choose coin" in reply.text
    await reply.buttons[0][0].click()
    wait()
    reply: Message = await conv.get_edit()
    assert f"{coin_name} amount is {coin_amount}" in reply.text
    await conv.send_message(str(coin_update_amount))
    wait()
    reply: Message = await conv.get_response()
    assert reply.text == f"Adding {coin_name} -> {float(coin_update_amount)}"
    await reply.buttons[0][0].click()
    wait()
    reply: Message = await conv.get_edit()
    assert reply.text == f"{coin_name} -> {float(coin_update_amount)} updated!"


@pytest.mark.asyncio
async def test_010_update_coin_with_invalid_data(conv: Conversation):
    reply: Message = await go_to_update_coin_menu(conv)
    wait()
    assert "Choose coin" in reply.text
    await reply.buttons[0][0].click()
    wait()
    await conv.send_message("NOT A VALID AMOUNT")

# @pytest.mark.asyncio
# async def test_010_all_back_buttons(conv: Conversation):
#     pass

# TODO tests:
#   - Return buttons
#   - Add multiple coins and test keyboard
