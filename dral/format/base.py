from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..generator import DralOutputFile


class BaseFormat(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def _make_default(self, objects: List[DralOutputFile], model: Optional[DralOutputFile]) -> None:
        pass

    @abstractmethod
    def _make_single(self, objects: List[DralOutputFile]) -> None:
        pass

    def make(self, objects: List[DralOutputFile], model: Optional[DralOutputFile] = None, single: bool = False) -> None:
        if single:
            self._make_single(objects)
        else:
            self._make_default(objects, model=model)
