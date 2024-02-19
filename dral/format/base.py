from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from ..generator import DralOutputFile


class BaseFormat(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def _make_default(self, objects: List[DralOutputFile], model: Optional[DralOutputFile] = None) -> None:
        pass

    def make(self, objects: List[DralOutputFile], model: Optional[DralOutputFile] = None) -> None:
        if model is None:
            self._make_default(objects)
        else:
            self._make_default(objects, model=model)
