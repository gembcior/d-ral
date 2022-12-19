from typing import Optional, Union, List

from ..types import Bank, Device, Peripheral, Register
from .base import BaseFilter


class WhiteListFilter(BaseFilter):
    def __init__(self, _list: Device) -> None:
        super().__init__()
        self._list = _list

    def _get_register(self, register: Register, registers: list[Register]) -> Optional[Register]:
        for item in registers:
            if item.name == register.name:
                return item
        return None

    def _get_bank(self, bank: Bank, banks: list[Bank]) -> Optional[Bank]:
        # TODO
        return None

    def _get_peripheral(self, peripheral: Peripheral, peripherals: list[Peripheral]) -> Optional[Peripheral]:
        registers = []
        for item in peripherals:
            if item.name == peripheral.name:
                for reg in peripheral.registers:
                    register = self._get_register(reg, item.registers)
                    if register is not None:
                        registers.append(register)
                if not registers:
                    registers = item.registers
                return Peripheral(name=item.name, description=item.description, address=item.address, registers=registers)
        return None

    def apply(self, device: Device) -> Device:
        peripherals = []
        for item in self._list.peripherals:
            peripheral = self._get_peripheral(item, device.peripherals)
            if peripheral is not None:
                peripherals.append(peripheral)
        return Device(name=device.name, description=device.description, peripherals=peripherals)

    def can_remove(self, item: Union[Peripheral, Register], _list: Union[List[Peripheral], List[Register]]) -> bool:
        for x in _list:
            if item.name == x.name:
                return False
        return True

    def _remove_registers(self):
        pass

    def _remove_peripherals(self):
        pass

    def apply2(self, device: Device) -> Device:
        for i in reversed(range(len(device.peripherals))):
            if self.can_remove(device.peripherals[i], self._list.peripherals):
                del device.peripherals[i]
