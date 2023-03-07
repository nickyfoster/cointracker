from cointracker.services.ExceptionCode import ExceptionCode
from cointracker.services.ExceptionMessage import ExceptionMessage


class CustomException(Exception):

    @property
    def code(self):
        return self.__code

    @property
    def message(self):
        return self.__message

    @property
    def arguments(self):
        return self.__arguments

    def __init__(self, code: ExceptionCode, message: ExceptionMessage, arguments: dict = None):
        self.__code = code
        self.__message = message
        self.__arguments = arguments

    def __str__(self):
        if self.__arguments:
            return f'[{self.__code.value}] {self.__message.value} {self.__arguments}'
        else:
            return f'[{self.__code.value}] {self.__message.value}'
