from abc import ABC
from typing import List

class BaseType(ABC):
    def __init__(self) -> None:
        self._name = ""
        self._description = ""

    def __eq__(self, other: 'BaseType') -> bool:
        if (other.name is not None) and (self._name is not None):
            if other.name != self._name:
                return False
        if (other.description is not None) and (self._description is not None):
            if other.description != self._description:
                return False
        return True

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description


class Field(BaseType):
    def __init__(self) -> None:
        self._position = 0
        self._mask = 0
        self._width = 0

    def __eq__(self, other: 'Field') -> bool:
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

    @property
    def position(self) -> int:
        return self._position

    @property
    def mask(self) -> int:
        return self._mask

    @property
    def width(self) -> int:
        return self._width


class Register(BaseType):
    def __init__(self) -> None:
        self._offset = 0
        self._size = 0
        self._access = ""
        self._reset_value = 0
        self._fields = []

    def __eq__(self, other: 'Register') -> bool:
        if not super().__eq__(other):
            return False
        return True

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def size(self) -> int:
        return self._size

    @property
    def access(self) -> str:
        return self._access

    @property
    def reset_value(self) -> int:
        return self._reset_value

    @property
    def fields(self) -> List[Field]:
        return self._fields


class Peripheral(BaseType):
    def __init__(self) -> None:
        self._address = 0
        self._registers = []

    def __eq__(self, other: 'Peripheral') -> bool:
        if not super().__eq__(other):
            return False
        return True

    @property
    def address(self) -> int:
        return self._address

    @property
    def registers(self) -> List[Register]:
        return self._registers


class Device(BaseType):
    def __init__(self) -> None:
        self._peripherals = []

    def __eq__(self, other: 'Device') -> bool:
        if not super().__eq__(other):
            return False
        if (other.peripherals is not None) and (self._peripherals is not None):
            if other.peripherals != self._peripherals:
                return False
        return True

    @property
    def peripherals(self) -> List[Peripheral]:
        return self._peripherals
