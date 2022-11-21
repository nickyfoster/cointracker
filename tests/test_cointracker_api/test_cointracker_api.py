import unittest

from services.Cointracker import Cointracker
from services.Exception import CustomException


class TestCointrackerAPI(unittest.TestCase):

    def test_001_invalid_coin_data(self):
        with self.assertRaises(CustomException):
            tracker = Cointracker()
            tracker.update_coins_data("Not List")
