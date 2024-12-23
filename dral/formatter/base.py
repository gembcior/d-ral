from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from dral.core.generator import DralOutputFile


class DralFormatter(ABC):
    def _get_style_dir(self) -> Path:
        return Path(__file__).parent / "style"

    @abstractmethod
    def format(self, objects: list[DralOutputFile]) -> list[DralOutputFile]:
        pass
