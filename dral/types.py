from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class DralBaseType(ABC):
    def __init__(self, name: str, description: Optional[str] = None):
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
    def description(self) -> Optional[str]:
        return self._description

    @abstractmethod
    def asdict(self) -> Dict[str, Any]:
        pass


class Field(DralBaseType):
    def __init__(self, name: str, description: Optional[str] = None, position: Optional[int] = None, width: Optional[int] = None) -> None:
        super().__init__(name, description)
        self._position = position
        self._width = width
        self._mask = (1 << width) - 1 if width is not None else None

    def asdict(self) -> Dict[str, Any]:
        return {
            "field": {
                "name": self._name,
                "description": self._description,
                "position": self._position,
                "width": self._width,
                "mask": self._mask,
            }
        }

    @property
    def position(self) -> Optional[int]:
        return self._position

    @property
    def mask(self) -> Optional[int]:
        return self._mask

    @property
    def width(self) -> Optional[int]:
        return self._width


class Register(DralBaseType):
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        offset: Optional[int] = None,
        size: Optional[int] = None,
        access: Optional[str] = None,
        reset_value: Optional[int] = None,
        fields: Optional[List[Field]] = None,
    ):
        super().__init__(name, description)
        self._offset = offset
        self._size = size
        self._access = access
        self._reset_value = reset_value
        if fields is None:
            fields = []
        self._fields = fields

    def asdict(self) -> Dict[str, Any]:
        return {
            "register": {
                "name": self._name,
                "description": self._description,
                "offset": self._offset,
                "size": self._size,
                "access": self._access,
                "reset_value": self._reset_value,
                "fields": [field.asdict() for field in self._fields],
            }
        }

    @property
    def offset(self) -> Optional[int]:
        return self._offset

    @property
    def size(self) -> Optional[int]:
        return self._size

    @property
    def access(self) -> Optional[str]:
        return self._access

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
        description: Optional[str] = None,
        offset: Optional[int] = None,
        size: Optional[int] = None,
        access: Optional[str] = None,
        reset_value: Optional[int] = None,
        bank_offset: Optional[int] = None,
        fields: Optional[List[Field]] = None,
    ):
        super().__init__(name, description, offset, size, access, reset_value, fields)
        self._bank_offset = bank_offset

    def asdict(self) -> Dict[str, Any]:
        return {
            "bank": {
                "name": self._name,
                "description": self._description,
                "offset": self._offset,
                "size": self._size,
                "access": self._access,
                "reset_value": self._reset_value,
                "bank_offset": self._bank_offset,
                "fields": [field.asdict() for field in self._fields],
            }
        }

    @property
    def bank_offset(self) -> Optional[int]:
        return self._bank_offset


class Peripheral(DralBaseType):
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        address: Optional[int] = None,
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
            "peripheral": {
                "name": self._name,
                "description": self._description,
                "address": self._address,
                "registers": [register.asdict() for register in self._registers],
                "banks": [bank.asdict() for bank in self._banks],
            }
        }

    @property
    def address(self) -> Optional[int]:
        return self._address

    @property
    def registers(self) -> List[Register]:
        return self._registers

    @property
    def banks(self) -> List[Bank]:
        return self._banks


class Device(DralBaseType):
    def __init__(self, name: str, description: Optional[str] = None, peripherals: Optional[List[Peripheral]] = None):
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
