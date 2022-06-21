from pathlib import Path
from typing import Dict, List

import svd2py

from ..types import Device, Field, Peripheral, Register
from .base import BaseAdapter


class SvdAdapter(BaseAdapter):
    def __init__(self, svd_file: Path) -> None:
        self._svd_file = svd_file

    def _get_fields(self, svd_fields: List[Dict]) -> List[Field]:
        fields_list = []
        for field in svd_fields:
            new_field = Field(
                    name = field["name"],
                    description = field["description"],
                    position = field["bitOffset"],
                    mask = ((1 << field["bitWidth"]) - 1),
                    width = field["bitWidth"])
            fields_list.append(new_field)
        return fields_list

    def _get_registers(self, svd_registers: List[Dict]) -> List[Register]:
        registers_list = []
        for register in svd_registers:
            fields = []
            if "fields" in register:
                fields = self._get_fields(register["fields"])
            new_register = Register(
                    name = register["name"],
                    description = register["description"],
                    offset = register["addressOffset"],
                    size = register["size"],
                    access = register["access"] if "access" in register else "",
                    reset_value = register["resetValue"],
                    fields = fields)
            registers_list.append(new_register)
        return registers_list

    def _get_peripherals(self, svd_peripherals: List[Dict]) -> List[Peripheral]:
        peripherals_list = []
        for peripheral in svd_peripherals:
            registers = []
            if "registers" in peripheral:
                if "register" in peripheral["registers"]:
                    registers = self._get_registers(peripheral["registers"]["register"])
            new_peripheral = Peripheral(
                    name = peripheral["name"],
                    description = peripheral["description"],
                    address = peripheral["baseAddress"],
                    registers = registers)
            peripherals_list.append(new_peripheral)
        return peripherals_list

    def _svd_to_dral(self, svd: Dict) -> Device:
        svd_device = svd["device"]
        device = Device(
                name = svd_device["name"],
                description = svd_device["description"],
                peripherals = self._get_peripherals(svd_device["peripherals"]))
        return device

    def convert(self) -> Device:
        svd = svd2py.SvdParser(self._svd_file)
        svd = svd.convert()
        return self._svd_to_dral(svd)
