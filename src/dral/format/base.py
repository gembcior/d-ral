from abc import ABC, abstractmethod
from typing import List


class BaseFormat(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _make_default(self, objects: List):
        pass

    @abstractmethod
    def _make_single(self, objects: List):
        pass

    def make(self, objects: List, single: bool=False):
        if single:
            self._make_single(objects)
        else:
            self._make_default(objects)
