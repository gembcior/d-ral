# =================================================================================
#
# MIT License
#
# Copyright (c) 2026 Gembcior
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# =================================================================================

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from dral.core.objects import (
    DralAccessType,
    DralDevice,
    DralField,
    DralGroup,
    DralGroupInstance,
    DralRegister,
)

from .base import BaseAdapter

DEFAULT_VALUE_TYPE = "uint32_t"

YAML_ACCESS_TYPE_MAPPING = {
    "ro": DralAccessType.ReadOnly,
    "wo": DralAccessType.WriteOnly,
    "wt": DralAccessType.ReadWrite,
    "rw": DralAccessType.ReadWrite,
    "const": DralAccessType.ReadOnly,
    "ext": DralAccessType.ReadWrite,
    "csr": DralAccessType.ReadWrite,
    "mrw": DralAccessType.ReadWrite,
    "rwx": DralAccessType.ReadWrite,
    "rot": DralAccessType.ReadOnly,
    "dwt": DralAccessType.ReadWrite,
    "brw": DralAccessType.ReadWrite,
}


class DralAdapter(BaseAdapter):
    def _get_access_type(self, access: str) -> DralAccessType:
        key = access.lower()
        if key not in YAML_ACCESS_TYPE_MAPPING:
            raise ValueError(f"Unknown access type: {access!r}. Expected one of {list(YAML_ACCESS_TYPE_MAPPING)}")
        return YAML_ACCESS_TYPE_MAPPING[key]

    def _get_dral_fields(self, fields_data: list[dict[str, Any]]) -> list[DralField]:
        fields = []
        for field in fields_data:
            fields.append(
                DralField(
                    name=field["name"],
                    description=field.get("description", ""),
                    access=self._get_access_type(field["access"]),
                    value_type=field.get("value_type", DEFAULT_VALUE_TYPE),
                    reset_value=field.get("reset_value", 0),
                    position=field["position"],
                    width=field["width"],
                )
            )
        return fields

    def _get_dral_registers(self, registers_data: list[dict[str, Any]]) -> list[DralRegister]:
        registers = []
        for register in registers_data:
            registers.append(
                DralRegister(
                    name=register["name"],
                    description=register.get("description", ""),
                    access=self._get_access_type(register["access"]),
                    value_type=register.get("value_type", DEFAULT_VALUE_TYPE),
                    address=int(register["address"]),
                    size=register["size"],
                    reset_value=register.get("reset_value", 0),
                    fields=self._get_dral_fields(register.get("fields", [])),
                )
            )
        return registers

    def _get_dral_groups(self, groups_data: list[dict[str, Any]]) -> list[DralGroup]:
        groups = []
        for group in groups_data:
            instances = [DralGroupInstance(name=inst["name"], address=inst["address"]) for inst in group.get("instances", [])]
            groups.append(
                DralGroup(
                    name=group["name"],
                    description=group.get("description", ""),
                    address=0,
                    offset=group.get("offset", 0),
                    instances=instances,
                    groups=self._get_dral_groups(group.get("groups", [])),
                    registers=self._get_dral_registers(group.get("registers", [])),
                )
            )
        return groups

    def convert(self, input_file: Path) -> DralDevice:
        # data = yaml.safe_load(input_file.read_text())
        data = yaml.load(input_file.read_text(), Loader=yaml.FullLoader)
        return DralDevice(
            name=data["name"],
            description=data.get("description", ""),
            address=data.get("address", 0),
            groups=self._get_dral_groups(data.get("groups", [])),
        )
