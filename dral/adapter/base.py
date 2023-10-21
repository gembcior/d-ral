from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from ..types import Device


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

    def __init__(self, _=Path) -> None:  # type: ignore[no-untyped-def]
        pass

    @abstractmethod
    def convert(self) -> Device:
        pass
