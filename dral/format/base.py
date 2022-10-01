from abc import ABC, abstractmethod
from typing import Dict, List


class BaseFormat(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def _make_default(self, objects: List[Dict[str, str]]) -> None:
        pass

    @abstractmethod
    def _make_single(self, objects: List[Dict[str, str]]) -> None:
        pass

    def make(self, objects: List[Dict[str, str]], single: bool = False) -> None:
        if single:
            self._make_single(objects)
        else:
            self._make_default(objects)
