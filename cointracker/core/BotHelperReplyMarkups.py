# TODO keep all keyboards here
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from cointracker.core.path_constants import GET_PORTFOLIO, UPDATE_MENU, PORTFOLIO_PRICE_UPDATE, START, UPDATE_PORTFOLIO, \
    ADD_COIN


class BotHelperReplyMarkups:
    def __init__(self):
        pass

    @staticmethod
    def get_inline_keyboard_markup_from_keyboard(keyboard):
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_keyboard(keyboard_layout):
        """
        keyboard_data = [
                {"Start": callback_data, "End": callback_data},
                {"Back": callback_data}
        ]
        """
        keyboard = [[] for _ in range(len(keyboard_layout))]

        for index, row in enumerate(keyboard_layout):
            for name, callback_data in row.items():
                keyboard[index].append(InlineKeyboardButton(name, callback_data=callback_data))
        return keyboard

    @staticmethod
    def get_coins_keyboard(coins, n_rows: int = 3):
        keyboard = [[] for _ in range(n_rows)]
        keyboard.append([InlineKeyboardButton("Back", callback_data=START)])
        cnt = 0
        for coin in coins:
            coin_symbol = str(coin)
            keyboard[cnt % n_rows].append(
                InlineKeyboardButton(coin_symbol.upper(),
                                     callback_data=f"{UPDATE_PORTFOLIO}_{coin_symbol.lower()}"))
            cnt += 1
        return keyboard

    def get_start_reply_markup(self):
        keyboard = self.get_keyboard(
            [{"Show Portfolio": GET_PORTFOLIO, "Update Portfolio": UPDATE_MENU}])
        return self.get_inline_keyboard_markup_from_keyboard(keyboard)

    def get_update_menu_reply_markup(self):
        keyboard = keyboard = self.get_keyboard(
            [{"Add coin": ADD_COIN, "Update coin": UPDATE_PORTFOLIO}, {"Back": START}])
        return self.get_inline_keyboard_markup_from_keyboard(keyboard)
