from __future__ import annotations

from typing import Union

from ..types import MultiPeripheralDevice, SinglePeripheralDevice
from .base import BaseFilter


class BlackListFilter(BaseFilter):
    def __init__(self, _list: Union[MultiPeripheralDevice, SinglePeripheralDevice]) -> None:
        super().__init__()
        self._list = _list

    def apply(self, device: Union[MultiPeripheralDevice, SinglePeripheralDevice]) -> Union[MultiPeripheralDevice, SinglePeripheralDevice]:
        return device
