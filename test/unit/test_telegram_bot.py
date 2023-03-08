import json
import unittest

from telegram import InlineKeyboardButton

from cointracker.core.Cointracker import Cointracker
from cointracker.services.Exception import CustomException
from cointracker.core.TelegramCointrackerBot import TelegramCointrackerBot
from unit.env import RESOURCES


class TestTelegramBotAPI(unittest.TestCase):
    COINS_KEYBOARD_DATA = RESOURCES / "telegram_bot/coins_list_for_keyboard.json"
    KEYBOARD_DATA = RESOURCES / "telegram_bot/keyboard_data.json"

    def test_000_coins_keyboard_generation(self):
        data = json.load(open(TestTelegramBotAPI.COINS_KEYBOARD_DATA))
        coins = data["coins"]
        n_rows = data["n_rows"]
        bot = TelegramCointrackerBot()
        keyboard = bot.get_coins_keyboard(coins=coins, n_rows=n_rows)
        assert len(keyboard[:-1]) == n_rows
        self.assertIsInstance(keyboard[-1][0], InlineKeyboardButton)
        assert type(keyboard) == list
        assert len(keyboard[-1]) == 1

        for row in keyboard[:-1]:
            for button in row:
                assert button["callback_data"].startswith("update_portfolio_")
                assert type(button["text"]) == str

    def test_001_keyboard_generation(self):
        keyboard_layout = json.load(open(TestTelegramBotAPI.KEYBOARD_DATA))
        bot = TelegramCointrackerBot()

        keyboard = bot.get_keyboard(keyboard_layout=keyboard_layout)
        assert len(keyboard) == len(keyboard_layout)

    def test_001_invalid_coin_data(self):
        with self.assertRaises(CustomException):
            tracker = Cointracker()
            tracker.update_coins_data("Invalid coin data")
