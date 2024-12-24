from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from enum import Enum
from typing import Any


class DralAccessType(Enum):
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
