import logging
from functools import partial
from typing import Union, Callable, List

from redis import Redis
from redis.exceptions import ConnectionError, ResponseError

from cointracker.DBConnectors.AbstractDBConnector import AbstractDBConnector
from cointracker.services.Config import DBConfig
from cointracker.services.Exception import CustomException
from cointracker.services.ExceptionCode import ExceptionCode
from cointracker.services.ExceptionMessage import ExceptionMessage


class RedisConnector(AbstractDBConnector):

    def __init__(self, config: DBConfig):
        self.config = config
        self.redis = self.init_redis()
        self.logger = logging.getLogger("main")
        self.user_prefix = None
        self.coin_prefix = "coin"

    def init_redis(self):
        return Redis(host=self.config.host,
                     port=self.config.port,
                     db=self.config.db,
                     password=self.config.password)

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

    def get_full_key(self, keyname: str) -> str:
        return f"{self.user_prefix}/{self.coin_prefix}/{keyname.lower()}"

    def set(self, key: str, data: Union) -> None:
        key = self.get_full_key(key)
        self.call(partial(self.redis.set, key, data))

    def get(self, key: str) -> str:
        key = self.get_full_key(key)
        return self.call(partial(self.redis.get, key))

    def exists(self, key: str) -> bool:
        key = self.get_full_key(key)
        return self.call(partial(self.redis.exists, key))

    def delete_key(self, key: str) -> None:
        key = self.get_full_key(key)
        self.call(partial(self.redis.delete, key))

    def delete_keys(self, keys: List[str]) -> None:
        for key in keys:
            self.call(partial(self.delete_key, key))

    def __list(self, keys_filter: str):
        return [key.decode() for key in self.redis.scan_iter(keys_filter)]

    def list(self, keys_filter: str = '') -> list:
        return self.call(partial(self.__list, keys_filter))

    def list_coin_keys(self):
        return self.list(keys_filter=f"{self.user_prefix}/{self.coin_prefix}/*")

    def set_user_prefix(self, prefix):
        self.user_prefix = str(prefix)

    def migrate(self):
        self.logger.info("Starting DB migration...")
        keys = self.list(keys_filter=f"{self.coin_prefix}/*")

        for key_fullname in keys:
            key_name = str(key_fullname).split("/")[1]
            key_data = self.call(partial(self.redis.get, key_fullname))
            self.set(key_name, key_data)
            self.call(partial(self.redis.delete, key_fullname))
        self.logger.info("DB successfully migrated")
