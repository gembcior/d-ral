from __future__ import annotations

from typing import List, Union

from ..types import MultiPeripheralDevice, SinglePeripheralDevice
from .base import BaseFilter


class ExcludeFilter(BaseFilter):
    def __init__(self, exclude: List[str]) -> None:
        self._exclude = exclude

    def apply(self, device: Union[MultiPeripheralDevice, SinglePeripheralDevice]) -> Union[MultiPeripheralDevice, SinglePeripheralDevice]:
        return device
