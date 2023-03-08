from abc import ABC, abstractmethod
from typing import Union


class AbstractDBConnector(ABC):

    @abstractmethod
    def get(self, key: str) -> str:
        pass

    @abstractmethod
    def set(self, key: str, data: Union) -> None:
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def delete_key(self, key: str) -> None:
        pass

    # @abstractmethod
    # def delete_keys(self, keys: List[str]) -> None:
    #     pass

    @abstractmethod
    def list(self, keys_filter: str = '') -> list:
        pass

    @abstractmethod
    def list_coin_keys(self):
        pass

    @abstractmethod
    def set_user_prefix(self, prefix):
        pass

    @abstractmethod
    def migrate(self):
        pass

    @abstractmethod
    def get_full_key(self, keyname: str) -> str:
        pass