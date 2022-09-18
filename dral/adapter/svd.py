import re
from pathlib import Path
from typing import Any, Dict, List

import svd2py

from ..types import Device, Field, Peripheral, Register
from .base import BaseAdapter


class IncorrectSvd(Exception):
    def __init__(self, *args: Any) -> None:
        super().__init__(args)


class SvdAdapter(BaseAdapter):
    def __init__(self, svd_file: Path) -> None:
        self._svd_file = svd_file

    def _get_fields(self, svd_fields: List[Dict[str, Any]]) -> List[Field]:
        fields_list = []
        for field in svd_fields:
            if "bitRange" in field:
                pattern = re.compile(r"(\d+):(\d+)")
                result = re.search(pattern, field["bitRange"])
                if result is not None:
                    position = int(result.group(2))
                    width = (int(result.group(1)) + 1) - position
                else:
                    raise IncorrectSvd("Determining the position and width of the field is impossible.")
            else:
                position = field["bitOffset"]
                width = field["bitWidth"]
            new_field = Field(
                name=field["name"],
                description=field["description"],
                position=position,
                mask=((1 << width) - 1),
                width=width,
            )
            fields_list.append(new_field)
        return fields_list

    def _get_registers(self, svd_registers: List[Dict[str, Any]]) -> List[Register]:
        registers_list = []
        for register in svd_registers:
            fields = []
            if "fields" in register:
                fields = self._get_fields(register["fields"])
            new_register = Register(
                name=register["name"],
                description=register["description"],
                offset=register["addressOffset"],
                size=register["size"],
                access=register["access"] if "access" in register else "",
                reset_value=register["resetValue"],
                fields=fields,
            )
            registers_list.append(new_register)
        return registers_list

    def _get_peripherals(self, svd_peripherals: List[Dict[str, Any]]) -> List[Peripheral]:
        peripherals_list = []
        for peripheral in svd_peripherals:
            registers = []
            if "registers" in peripheral:
                if "register" in peripheral["registers"]:
                    registers = self._get_registers(peripheral["registers"]["register"])
            new_peripheral = Peripheral(
                name=peripheral["name"],
                description=peripheral["description"],
                address=peripheral["baseAddress"],
                registers=registers,
            )
            peripherals_list.append(new_peripheral)
        return peripherals_list

    def _svd_to_dral(self, svd: Dict[str, Any]) -> Device:
        svd_device = svd["device"]
        device = Device(
            name=svd_device["name"],
            description=svd_device["description"],
            peripherals=self._get_peripherals(svd_device["peripherals"]),
        )
        return device

    def convert(self) -> Device:
        svd = svd2py.SvdParser(self._svd_file)
        svd = svd.convert()
        return self._svd_to_dral(svd)
