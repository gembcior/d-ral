from ..types import Device, Peripheral
from .base import BaseFilter


class WhiteListFilter(BaseFilter):
    def __init__(self, _list: Device) -> None:
        super().__init__()
        self._list = _list

    def apply(self, device: Device) -> Device:
        # TODO simplify
        new_peripheral_list = []
        for peripheral in self._list.peripherals:
            for item in device.peripherals:
                if item.name == peripheral.name:
                    if peripheral.registers:
                        new_registers_list = []
                        for register in peripheral.registers:
                            for reg_item in item.registers:
                                if reg_item.name == register.name:
                                    new_registers_list.append(reg_item)
                        new_peripheral = Peripheral(
                            name=item.name,
                            description=item.description,
                            address=item.address,
                            registers=new_registers_list,
                        )
                        new_peripheral_list.append(new_peripheral)
                    else:
                        new_peripheral_list.append(item)
        return Device(
            name=device.name,
            description=device.description,
            peripherals=new_peripheral_list,
        )
