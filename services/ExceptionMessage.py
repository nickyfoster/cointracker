from enum import Enum


class ExceptionMessage(Enum):
    URL_INVALID = 'cointracker.url.invalid'
    COINTRACKER_DB_REDIS_UNABLE_TO_CONNECT = 'cointracker.db.unable_to_connect_to_redis_db'
    COINTRACKER_DB_REDIS_WRONG_PASS = 'cointracker.db.wrong_password_for_redis_db'
