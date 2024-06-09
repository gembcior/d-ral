from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any


@dataclass
class DralObject:
    name: str
    description: str = dataclasses.field(kw_only=True, default="")
    dral_object: str = dataclasses.field(kw_only=True, default="DralObject")

    def __post_init__(self):
        self.dral_object = self.__class__.__name__

    def asdict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class DralField(DralObject):
    position: int
    mask: int
    width: int


@dataclass
class DralRegister(DralObject):
    address: int
    size: int
    default: int
    fields: list[DralField] = dataclasses.field(default_factory=list)


@dataclass
class DralGroupInstance(DralObject):
    address: int


@dataclass
class DralGroup(DralObject):
    address: int
    offset: int
    instances: list[str] = dataclasses.field(default_factory=list)
    groups: list[DralGroup] = dataclasses.field(default_factory=list)
    registers: list[DralRegister] = dataclasses.field(default_factory=list)


@dataclass
class DralDevice(DralObject):
    groups: list[DralGroup] = dataclasses.field(default_factory=list)
