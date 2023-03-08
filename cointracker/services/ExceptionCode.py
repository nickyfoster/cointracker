from enum import Enum


class ExceptionCode(Enum):
    NOT_FOUND = 404
    BAD_REQUEST = 400
    INTERNAL_SERVER_ERROR = 500
    OK = 200
