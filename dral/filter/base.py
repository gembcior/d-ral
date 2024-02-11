from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Union

from ..types import MultiPeripheralDevice, SinglePeripheralDevice


class BaseFilter(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def apply(self, device: Union[MultiPeripheralDevice, SinglePeripheralDevice]) -> Union[MultiPeripheralDevice, SinglePeripheralDevice]:
        pass
