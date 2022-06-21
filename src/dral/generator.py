from pathlib import Path
from typing import Dict, List, Union, overload

from .objects import DralDevice
from .types import Device, Peripheral
from .utils import Utils


class Generator:
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, template: str) -> None:
        ...
    @overload
    def __init__(self, template: str, template_path: Path) -> None:
        ...
    def __init__(self, template = "default", template_path = None):
        self._utils = Utils(template, template_path)

    def _get_register_model_content(self):
        model = self._utils.get_template("model.dral")
        with open(model, "r") as f:
            return f.read()

    def _white_list_filter(self, data: Device, list: Device) -> Device:
        # TODO simplify
        new_peripheral_list = []
        for peripheral in list.peripherals:
            for item in data.peripherals:
                if item.name == peripheral.name:
                    if peripheral.registers:
                        new_registers_list = []
                        for register in peripheral.registers:
                            for reg_item in item.registers:
                                if reg_item.name == register.name:
                                    new_registers_list.append(reg_item)
                        new_peripheral = Peripheral(name=item.name, description=item.description, address=item.address, registers=new_registers_list)
                        new_peripheral_list.append(new_peripheral)
                    else:
                        new_peripheral_list.append(item)
        return Device(name=data.name, description=data.description, peripherals=new_peripheral_list)

    def _black_list_filter(self, data: Device, list: Device) -> Device:
        # TODO implement black list filtering
        return data

    def generate(self, device: Device, exclude: List[str] = [], white_list: Union[Device, None] = None, black_list: Union[Device, None] = None) -> List[Dict]:
        if white_list:
            device = self._white_list_filter(device, white_list)
        if black_list:
            device = self._black_list_filter(device, black_list)
        dral_device = DralDevice(device, utils=self._utils, exclude=exclude)
        objects = dral_device.parse()
        if self._utils.get_template("model.dral").exists():
            objects.append({"name": "register_model", "content": self._get_register_model_content()})
        return objects
