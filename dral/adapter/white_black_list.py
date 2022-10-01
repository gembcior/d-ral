from pathlib import Path
from typing import Any, Dict, List

import yaml

from ..types import Device, Field, Peripheral, Register
from .base import BaseAdapter


class WhiteBlackListAdapter(BaseAdapter):
    def __init__(self, list_file: Path) -> None:
        self._list_file = list_file

    def _get_fields(self, list_fields: List[Dict[str, Any]]) -> List[Field]:
        fields_list = []
        for field in list_fields:
            new_field = Field(**field)
            fields_list.append(new_field)
        return fields_list

    def _get_registers(self, list_registers: List[Dict[str, Any]]) -> List[Register]:
        registers_list = []
        for register in list_registers:
            if "fields" in register:
                register.update({"fields": self._get_fields(register["fields"])})
            new_register = Register(**register)
            registers_list.append(new_register)
        return registers_list

    def _get_peripherals(self, list_peripherals: List[Dict[str, Any]]) -> List[Peripheral]:
        peripherals_list = []
        for peripheral in list_peripherals:
            if "registers" in peripheral:
                peripheral.update({"registers": self._get_registers(peripheral["registers"])})
            new_peripheral = Peripheral(**peripheral)
            peripherals_list.append(new_peripheral)
        return peripherals_list

    def _list_to_dral(self, _list: Dict[str, Any]) -> Device:
        if "peripherals" in _list:
            _list.update({"peripherals": self._get_peripherals(_list["peripherals"])})
        return Device(**_list)

    def convert(self) -> Device:
        with open(self._list_file, "r", encoding="UTF-8") as list_file:
            _list = yaml.load(list_file, Loader=yaml.FullLoader)
        return self._list_to_dral(_list)
