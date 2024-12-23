from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from dral.core.objects import DralDevice


class BaseAdapter(ABC):
    """
    Abstract class for dral generator adapters

    Every adapter should inherit from this class and implement convert method.
    It should return Device object.

    ...

    Methods
    -------
    convert()
        Returns data structure used by d-ral generator
    """

    @abstractmethod
    def convert(self, input_file: Path) -> DralDevice:
        pass
