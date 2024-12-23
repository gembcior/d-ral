from __future__ import annotations

from abc import ABC, abstractmethod

from dral.core.generator import DralOutputFile


class DralLayout(ABC):
    @abstractmethod
    def make(self, objects: list[DralOutputFile], device: str) -> None:
        pass
