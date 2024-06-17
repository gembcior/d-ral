from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any


@dataclass
class DralObject:
    name: str
    description: str = dataclasses.field(kw_only=True, default="")
    dral_object: str = dataclasses.field(kw_only=True, default="DralObject")
    parent: list[str] = dataclasses.field(kw_only=True, default_factory=list)

    def __post_init__(self):
        self.dral_object = self.__class__.__name__

    def asdict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class DralField(DralObject):
    position: int
    mask: int
    width: int

    def link_parent(self, parent: list[str] | None = None) -> None:
        self.parent = parent if parent is not None else []


@dataclass
class DralRegister(DralObject):
    address: int
    size: int
    default: int
    fields: list[DralField] = dataclasses.field(default_factory=list)

    def link_parent(self, parent: list[str] | None = None) -> None:
        self.parent = parent if parent is not None else []
        for child in self.fields:
            child.link_parent(self.parent + [self.name])


@dataclass
class DralGroupInstance(DralObject):
    address: int

    def link_parent(self, parent: list[str] | None = None) -> None:
        self.parent = parent if parent is not None else []


@dataclass
class DralGroup(DralObject):
    address: int
    offset: list[int] | int
    instances: list[DralGroupInstance] = dataclasses.field(default_factory=list)
    groups: list[DralGroup] = dataclasses.field(default_factory=list)
    registers: list[DralRegister] = dataclasses.field(default_factory=list)

    def link_parent(self, parent: list[str] | None = None) -> None:
        self.parent = parent if parent is not None else []
        for child in self.registers + self.groups + self.instances:
            child.link_parent(self.parent + [self.name])


@dataclass
class DralDevice(DralObject):
    groups: list[DralGroup] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self.link_parent()

    def link_parent(self, parent: list[str] | None = None) -> None:
        self.parent = parent if parent is not None else []
        for child in self.groups:
            child.link_parent(self.parent + [self.name])
