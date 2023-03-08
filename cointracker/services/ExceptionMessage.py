from enum import Enum


class ExceptionMessage(Enum):
    URL_INVALID = "cointracker.url.invalid"
    NOT_IMPLEMENTED = "cointracker.not_implemented_yet"
    COINTRACKER_DB_REDIS_UNABLE_TO_CONNECT = "cointracker.db.unable_to_connect_to_redis_db"
    COINTRACKER_DB_REDIS_WRONG_PASS = "cointracker.db.wrong_password_for_redis_db"
    COINTRACKER_DATA_PORTFOLIO_DATA_EMPTY = "cointracker.data.portfolio_data_empty"
    COINTRACKER_DATA_PORTFOLIO_DATA_INVALID = "cointracker.data.portfolio_data_invalid"
    