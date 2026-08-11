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

import dataclasses
from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class DralAccessType(IntEnum):
    ReadOnly = 0
    WriteOnly = 1
    ReadWrite = 2


@dataclass
class DralSuffix:
    group: str = "group"
    register: str = "register"
    field: str = "field"

    def asdict(self) -> dict[str, str]:
        return dataclasses.asdict(self)


@dataclass
class DralParentObject:
    name: str
    address: int
    instances: list[DralGroupInstance] = dataclasses.field(default_factory=list)
    offset: list[int] | int = 0


@dataclass
class DralGroupInstance:
    name: str
    address: int


@dataclass
class DralObject:
    name: str
    description: str = dataclasses.field(kw_only=True, default="")
    dral_object: str = dataclasses.field(kw_only=True, default="DralObject")
    parent: list[DralParentObject] = dataclasses.field(kw_only=True, default_factory=list)

    def __post_init__(self) -> None:
        self.dral_object = self.__class__.__name__

    def asdict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def flat(self) -> DralObject:
        return dataclasses.replace(self)

    def link_parent(self, parent: list[DralParentObject] | None = None) -> None:
        _ = parent
        raise NotImplementedError(f"link_parent is not implemented for {self.__class__.__name__}")


@dataclass
class DralConcreteObject(DralObject):
    access: DralAccessType
    value_type: str
    reset_value: int = dataclasses.field(kw_only=True, default=0)


@dataclass
class DralField(DralConcreteObject):
    position: int
    width: int

    def link_parent(self, parent: list[DralParentObject] | None = None) -> None:
        self.parent = parent if parent is not None else []


@dataclass
class DralRegister(DralConcreteObject):
    address: int
    size: int
    fields: list[DralField] = dataclasses.field(default_factory=list)

    def __post_init__(self) -> None:
        super().__post_init__()
        for field in self.fields:
            field.reset_value = (self.reset_value >> field.position) & ((1 << field.width) - 1)

    def link_parent(self, parent: list[DralParentObject] | None = None) -> None:
        self.parent = parent if parent is not None else []
        for child in self.fields:
            child.link_parent(self.parent + [DralParentObject(self.name, self.address, [])])


@dataclass
class DralGroup(DralObject):
    address: int
    offset: list[int] | int
    instances: list[DralGroupInstance] = dataclasses.field(default_factory=list)
    groups: list[DralGroup] = dataclasses.field(default_factory=list)
    registers: list[DralRegister] = dataclasses.field(default_factory=list)

    def link_parent(self, parent: list[DralParentObject] | None = None) -> None:
        self.parent = parent if parent is not None else []
        for child in self.registers + self.groups:
            child.link_parent(self.parent + [DralParentObject(self.name, self.address, self.instances, self.offset)])

    def _collect_registers(self, base_offset: int = 0, name_prefix: str = "") -> list[DralRegister]:
        result = []
        for reg in self.registers:
            new_address: int = base_offset + reg.address
            result.append(dataclasses.replace(reg, name=f"{name_prefix}{reg.name}", address=new_address))
        for subgroup in self.groups:
            if subgroup.instances:
                for instance in subgroup.instances:
                    result.extend(
                        subgroup._collect_registers(
                            base_offset + instance.address,
                            name_prefix=f"{name_prefix}{instance.name}_",
                        )
                    )
            else:
                result.extend(
                    subgroup._collect_registers(
                        base_offset + subgroup.address,
                        name_prefix=f"{name_prefix}{subgroup.name}_",
                    )
                )
        return result

    def flat(self) -> list[DralGroup]:  # type: ignore[override]
        registers = self._collect_registers()
        return [
            DralGroup(
                name=self.name,
                description=self.description,
                address=instance.address,
                offset=0,
                instances=[],
                groups=[],
                registers=[dataclasses.replace(reg, name=f"{instance.name}_{reg.name}", address=instance.address + reg.address) for reg in registers],
            )
            for instance in self.instances
        ]


@dataclass
class DralDevice(DralObject):
    groups: list[DralGroup] = dataclasses.field(default_factory=list)
    address: int = 0

    def __post_init__(self) -> None:
        super().__post_init__()
        self.link_parent()

    def link_parent(self, parent: list[DralParentObject] | None = None) -> None:
        self.parent = parent if parent is not None else []
        for child in self.groups:
            child.link_parent(self.parent + [DralParentObject(self.name, self.address, [])])

    def sort(self) -> None:
        def _address_key(r: DralRegister) -> int:
            return r.address if isinstance(r.address, int) else 0  # type: ignore[return-value]

        def _group_key(g: DralGroup) -> int:
            return _address_key(g.registers[0]) if g.registers else g.address

        for group in self.groups:
            group.registers.sort(key=_address_key)
        self.groups.sort(key=_group_key)

    def flat(self) -> DralDevice:
        all_registers = sorted(
            [reg for group in self.groups for g in group.flat() for reg in g.registers],
            key=lambda r: r.address if isinstance(r.address, int) else 0,  # type: ignore[return-value]
        )
        flat_group = DralGroup(
            name=self.name,
            description=self.description,
            address=0,
            offset=0,
            instances=[],
            groups=[],
            registers=all_registers,
        )
        return DralDevice(
            name=self.name,
            description=self.description,
            address=self.address,
            groups=[flat_group],
        )
