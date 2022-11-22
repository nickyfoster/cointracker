from functools import partial
from typing import Union, Callable, List

from redis import Redis
from redis.exceptions import ConnectionError, ResponseError

from DBConnectors.AbstractDBConnector import AbstractDBConnector
from services.Config import DBConfig
from services.Exception import CustomException
from services.ExceptionCode import ExceptionCode
from services.ExceptionMessage import ExceptionMessage


class RedisConnector(AbstractDBConnector):

    def __init__(self, config: DBConfig):
        self.config = config
        self.redis = self.init_redis()

    def init_redis(self):
        try:
            return Redis(host=self.config.host,
                         port=self.config.port,
                         db=self.config.db,
                         password=self.config.password)

        except Exception as e:
            print(e)

    def set_redis(self):
        self.redis.close()
        self.redis = self.init_redis()

    def call(self, fnc: Callable):
        try:
            return fnc()
        except ConnectionError:
            raise CustomException(code=ExceptionCode.INTERNAL_SERVER_ERROR,
                                  message=ExceptionMessage.COINTRACKER_DB_REDIS_UNABLE_TO_CONNECT)
        except ResponseError:
            raise CustomException(code=ExceptionCode.INTERNAL_SERVER_ERROR,
                                  message=ExceptionMessage.COINTRACKER_DB_REDIS_WRONG_PASS)

    def close(self) -> None:
        self.call(self.redis.close)

    def set(self, key: str, data: Union) -> None:
        self.call(partial(self.redis.set, key, data))

    def get(self, key: str) -> str:
        return self.call(partial(self.redis.get, key))

    def exists(self, key: str) -> bool:
        return self.call(partial(self.redis.exists, key))

    def delete_key(self, key: str) -> None:
        self.call(partial(self.redis.delete, key))

    def delete_keys(self, keys: List[str]) -> None:
        for key in keys:
            self.call(partial(self.delete_key, key))

    def list(self, keys_filter: str = '') -> list:
        return [key.decode() for key in self.call(partial(self.redis.scan_iter, keys_filter))]
