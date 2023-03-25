from __future__ import annotations

from typing import List, Optional, Union

from ..types import Device, Peripheral, Register
from .base import BaseFilter


class WhiteListFilter(BaseFilter):
    def __init__(self, _list: Device) -> None:
        super().__init__()
        self._list = _list

    def can_remove(self, item: Union[Peripheral, Register], _list: Union[List[Peripheral], List[Register]]) -> bool:
        for x in _list:
            if item.name == x.name:
                return False
        return True

    def find_peripheral(self, item: Peripheral, _list: List[Peripheral]) -> Optional[Peripheral]:
        for x in _list:
            if item.name == x.name:
                return x
        return None

    def apply(self, device: Device) -> Device:
        for i in reversed(range(len(device.peripherals))):
            if self.can_remove(device.peripherals[i], self._list.peripherals):
                del device.peripherals[i]
            else:
                peripheral = self.find_peripheral(device.peripherals[i], self._list.peripherals)
                if peripheral is not None:
                    for j in reversed(range(len(device.peripherals[i].registers))):
                        if self.can_remove(device.peripherals[i].registers[j], peripheral.registers):
                            del device.peripherals[i].registers[j]
        return device
