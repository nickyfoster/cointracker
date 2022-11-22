from abc import ABC, abstractmethod
from typing import Union


class AbstractDBConnector(ABC):

    @abstractmethod
    def get(self, key: str) -> str:
        pass

    @abstractmethod
    def set(self, key: str, data: Union) -> None:
        pass
