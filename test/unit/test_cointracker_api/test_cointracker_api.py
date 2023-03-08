import unittest

from cointracker.core.Cointracker import Cointracker
from cointracker.services.Exception import CustomException


class TestCointrackerAPI(unittest.TestCase):
    def test_001_invalid_coin_data(self):
        with self.assertRaises(CustomException):
            tracker = Cointracker()
            tracker.update_coins_data("Invalid coin data")
