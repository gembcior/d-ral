from __future__ import annotations

from abc import ABC, abstractmethod

from ..generator import DralOutputFile


class DralLayout(ABC):
    @abstractmethod
    def make(self, objects: list[DralOutputFile]) -> None:
        pass
