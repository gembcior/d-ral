from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DralBaseType(ABC):
    def __init__(self, name: str, description: str = ""):
        self._name = name
        self._description = description

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DralBaseType):
            return NotImplemented
        for key, value in vars(other).items():
            if getattr(self, key) != value:
                return False
        return True

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @abstractmethod
    def asdict(self) -> Dict[str, Any]:
        pass


class Field(DralBaseType):
    def __init__(self, name: str, position: int, width: int, description: str = "") -> None:
        super().__init__(name, description)
        self._position = position
        self._width = width
        self._mask = (1 << width) - 1

    def asdict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "description": self._description,
            "position": self._position,
            "width": self._width,
            "mask": self._mask,
        }

    @property
    def position(self) -> int:
        return self._position

    @property
    def mask(self) -> int:
        return self._mask

    @property
    def width(self) -> int:
        return self._width


class Register(DralBaseType):
    def __init__(
        self,
        name: str,
        offset: int,
        size: int = 32,
        description: str = "",
        reset_value: Optional[int] = None,
        fields: Optional[List[Field]] = None,
        **custom_data,
    ):
        super().__init__(name, description)
        self._offset = offset
        if size not in [8, 16, 32, 64]:
            raise ValueError
        self._size = size
        self._reset_value = reset_value
        if fields is None:
            fields = []
        self._fields = fields
        self._custom_data = custom_data

    def asdict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "description": self._description,
            "offset": self._offset,
            "size": self._size,
            "reset_value": self._reset_value,
            "fields": [field.asdict() for field in self._fields],
            **self._custom_data,
        }

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def size(self) -> int:
        return self._size

    @property
    def reset_value(self) -> Optional[int]:
        return self._reset_value

    @property
    def fields(self) -> List[Field]:
        return self._fields


class Bank(Register):
    def __init__(
        self,
        name: str,
        offset: int,
        bank_offset: int,
        size: int = 32,
        description: str = "",
        reset_value: Optional[int] = None,
        fields: Optional[List[Field]] = None,
    ):
        super().__init__(name, offset, size, description, reset_value, fields)
        self._bank_offset = bank_offset

    def asdict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "description": self._description,
            "offset": self._offset,
            "size": self._size,
            "reset_value": self._reset_value,
            "bank_offset": self._bank_offset,
            "fields": [field.asdict() for field in self._fields],
        }

    @property
    def bank_offset(self) -> int:
        return self._bank_offset


class Peripheral(DralBaseType):
    def __init__(
        self,
        name: str,
        address: int = 0,
        description: str = "",
        registers: Optional[List[Register]] = None,
        banks: Optional[List[Bank]] = None,
    ):
        super().__init__(name, description)
        self._address = address
        if registers is None:
            registers = []
        self._registers = registers
        if banks is None:
            banks = []
        self._banks = banks

    def asdict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "description": self._description,
            "address": self._address,
            "registers": [register.asdict() for register in self._registers],
            "banks": [bank.asdict() for bank in self._banks],
        }

    @property
    def address(self) -> int:
        return self._address

    @property
    def registers(self) -> List[Register]:
        return self._registers

    @property
    def banks(self) -> List[Bank]:
        return self._banks


class Device(DralBaseType):
    def __init__(self, name: str, description: str = "", peripherals: Optional[List[Peripheral]] = None):
        super().__init__(name, description)
        if peripherals is None:
            peripherals = []
        self._peripherals = peripherals

    def asdict(self) -> Dict[str, Any]:
        return {
            "device": {
                "name": self._name,
                "description": self._description,
                "peripherals": [peripheral.asdict() for peripheral in self._peripherals],
            }
        }

    @property
    def peripherals(self) -> List[Peripheral]:
        return self._peripherals
