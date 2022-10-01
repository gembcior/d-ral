from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

import yaml


class BaseType(ABC):
    def __init__(self, name: str, description: str = ""):
        self._name = name
        self._description = description

    def __str__(self) -> str:
        return str(yaml.dump(self.asdict()))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseType):
            return NotImplemented
        if other.name != self._name:
            return False
        if other.description != self._description:
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


class Field(BaseType):
    def __init__(
        self,
        name: str,
        description: str = "",
        position: Union[None, int] = None,
        mask: Union[None, int] = None,
        width: Union[None, int] = None,
    ) -> None:
        super().__init__(name, description)
        self._position = position
        self._mask = mask
        self._width = width

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Field):
            return NotImplemented
        if not super().__eq__(other):
            return False
        if (other.position is not None) and (self._position is not None):
            if other.position != self._position:
                return False
        if (other.mask is not None) and (self._mask is not None):
            if other.mask != self._mask:
                return False
        if (other.width is not None) and (self._width is not None):
            if other.width != self._width:
                return False
        return True

    def asdict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "description": self._description,
            "position": self._position,
            "width": self._width,
            "mask": self._mask,
        }

    @property
    def position(self) -> Union[None, int]:
        return self._position

    @property
    def mask(self) -> Union[None, int]:
        return self._mask

    @property
    def width(self) -> Union[None, int]:
        return self._width


class Register(BaseType):
    def __init__(
        self,
        name: str,
        description: str = "",
        offset: Union[None, int] = None,
        size: Union[None, int] = None,
        access: Union[None, str] = None,
        reset_value: Union[None, int] = None,
        fields: Union[None, List[Field]] = None,
    ):
        super().__init__(name, description)
        self._offset = offset
        self._size = size
        self._access = access
        self._reset_value = reset_value
        if fields is None:
            fields = []
        self._fields = fields

    def __eq__(self, other: object) -> bool:  # noqa
        if not isinstance(other, Register):
            return NotImplemented
        if not super().__eq__(other):
            return False
        if (other.offset is not None) and (self._offset is not None):
            if other.offset != self._offset:
                return False
        if (other.size is not None) and (self._size is not None):
            if other.size != self._size:
                return False
        if (other.access is not None) and (self._access is not None):
            if other.access != other._access:
                return False
        if (other.reset_value is not None) and (self._reset_value is not None):
            if other.reset_value != other._reset_value:
                return False
        if other.fields and self.fields:
            if other.fields != other._fields:
                return False
        return True

    def asdict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "description": self._description,
            "offset": self._offset,
            "size": self._size,
            "access": self._access,
            "reset_value": self._reset_value,
            "fields": [field.asdict() for field in self._fields],
        }

    @property
    def offset(self) -> Union[None, int]:
        return self._offset

    @property
    def size(self) -> Union[None, int]:
        return self._size

    @property
    def access(self) -> Union[None, str]:
        return self._access

    @property
    def reset_value(self) -> Union[None, int]:
        return self._reset_value

    @property
    def fields(self) -> List[Field]:
        return self._fields


class Bank(Register):
    def __init__(
        self,
        name: str,
        description: str = "",
        offset: Union[None, int] = None,
        size: Union[None, int] = None,
        access: Union[None, str] = None,
        reset_value: Union[None, int] = None,
        bank_offset: Union[None, int] = None,
        fields: Union[None, List[Field]] = None,
    ):
        super().__init__(name, description, offset, size, access, reset_value, fields)
        self._bank_offset = bank_offset

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bank):
            return NotImplemented
        if not super().__eq__(other):
            return False
        if (other.bank_offset is not None) and (self._bank_offset is not None):
            if other.bank_offset != self._bank_offset:
                return False
        return True

    @property
    def bank_offset(self) -> Union[None, int]:
        return self._bank_offset


class Peripheral(BaseType):
    def __init__(
        self,
        name: str,
        description: str = "",
        address: Union[None, int] = None,
        registers: Union[None, List[Register]] = None,
        banks: Union[None, List[Bank]] = None,
    ):
        super().__init__(name, description)
        self._address = address
        if registers is None:
            registers = []
        self._registers = registers
        if banks is None:
            banks = []
        self._banks = banks

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Peripheral):
            return NotImplemented
        if not super().__eq__(other):
            return False
        if (other.address is not None) and (self._address is not None):
            if other.address != self._address:
                return False
        if other.registers and self._registers:
            if other.registers != self._registers:
                return False
        if other.banks and self._banks:
            if other.banks != self._banks:
                return False
        return True

    def asdict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "description": self._description,
            "address": self._address,
            "registers": [register.asdict() for register in self._registers],
        }

    @property
    def address(self) -> Union[None, int]:
        return self._address

    @property
    def registers(self) -> List[Register]:
        return self._registers

    @property
    def banks(self) -> List[Bank]:
        return self._banks


class Device(BaseType):
    def __init__(self, name: str, description: str = "", peripherals: Union[None, List[Peripheral]] = None):
        super().__init__(name, description)
        if peripherals is None:
            peripherals = []
        self._peripherals = peripherals

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Device):
            return NotImplemented
        if not super().__eq__(other):
            return False
        if other.peripherals and self._peripherals:
            if other.peripherals != self._peripherals:
                return False
        return True

    def asdict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "description": self._description,
            "peripherals": [peripheral.asdict() for peripheral in self._peripherals],
        }

    @property
    def peripherals(self) -> List[Peripheral]:
        return self._peripherals
