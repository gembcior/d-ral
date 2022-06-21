from typing import List, overload


class BaseType:
    @overload
    def __init__(self, name: None, description: None) -> None:
        ...
    @overload
    def __init__(self, name: str, description: str) -> None:
        ...
    def __init__(self, name = None, description = None):
        self._name = name
        self._description = description

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
    @overload
    def __init__(self, name: None, description: None, position: None, mask: None, width: None) -> None:
        ...
    @overload
    def __init__(self, name: str, description: str, position: int, mask: int, width: int) -> None:
        ...
    def __init__(self, name = None, description = None, position = None, mask = None, width = None):
        super().__init__(name, description)
        self._position = position
        self._mask = mask
        self._width = width

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

    def __str__(self) -> str:
        # TODO consider something more sophisticated
        return f"{self._name} | {self._position} | {self._width} | 0x{self._mask:02X}"

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
    @overload
    def __init__(self, name: None, description: None, offset: None, size: None, access: None, reset_value: None, fields: None) -> None:
        ...
    @overload
    def __init__(self, name: str, description: str, offset: int, size: int, access: str, reset_value: int, fields: List[Field]) -> None:
        ...
    def __init__(self, name = None, description = None, offset = None, size = None, access = None, reset_value = None, fields = None):
        super().__init__(name, description)
        self._offset = offset
        self._size = size
        self._access = access
        self._reset_value = reset_value
        self._fields = fields

    def __eq__(self, other: 'Register') -> bool:
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
        if (other.fields is not None) and (self.fields is not None):
            if other.fields != other._fields:
                return False
        return True

    def __str__(self) -> str:
        # TODO consider something more sophisticated
        register = f"{self._name} | {self._offset} | {self._size}\n"
        if self._fields:
            for field in self._fields:
                register += f"    {field}\n"
        return register

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


class RegisterBank(Register):
    @overload
    def __init__(self, name: None, description: None, offset: None, size: None, access: None, reset_value: None, bank_offset: None, fields: None) -> None:
        ...
    @overload
    def __init__(self, name: str, description: str, offset: int, size: int, access: str, reset_value: int, bank_offset: int, fields: List[Field]) -> None:
        ...
    def __init__(self, name = None, description = None, offset = None, size = None, access = None, reset_value = None, bank_offset = None, fields = None):
        super().__init__(name, description, offset, size, access, reset_value, fields)
        self._bank_offset = bank_offset

    def __eq__(self, other: 'RegisterBank') -> bool:
        if not super().__eq__(other):
            return False
        if (other.bank_offset is not None) and (self._bank_offset is not None):
            if other.bank_offset != self._bank_offset:
                return False
        return True

    def __str__(self) -> str:
        # TODO consider something more sophisticated
        register = f"{self._name} | {self._offset} | {self._size} | {self._bank_offset}\n"
        if self._fields:
            for field in self._fields:
                register += f"    {field}\n"
        return register

    @property
    def bank_offset(self) -> int:
        return self._bank_offset


class Peripheral(BaseType):
    @overload
    def __init__(self, name: None, description: None, address: None, registers: None) -> None:
        ...
    @overload
    def __init__(self, name: str, description: str, address: int, registers: List[Register]) -> None:
        ...
    def __init__(self, name = None, description = None, address = None, registers = None):
        super().__init__(name, description)
        self._address = address
        self._registers = registers

    def __eq__(self, other: 'Peripheral') -> bool:
        if not super().__eq__(other):
            return False
        if (other.address is not None) and (self._address is not None):
            if other.address != self._address:
                return False
        if (other.registers is not None) and (self._registers is not None):
            if other.registers != self._registers:
                return False
        return True

    def __str__(self) -> str:
        # TODO consider something more sophisticated
        peripheral = f"{self._name} | {self._address:08X}\n"
        if self._registers:
            for register in self._registers:
                for substr in str(register).split('\n'):
                    peripheral += f"    {substr}\n"
        return peripheral

    @property
    def address(self) -> int:
        return self._address

    @property
    def registers(self) -> List[Register]:
        return self._registers


class Device(BaseType):
    @overload
    def __init__(self, name: None, description: None, peripherals: None):
        ...
    @overload
    def __init__(self, name: str, description: str, peripherals: List[Peripheral]):
        ...
    def __init__(self, name = None, description = None, peripherals = None):
        super().__init__(name, description)
        self._peripherals = peripherals

    def __eq__(self, other: 'Device') -> bool:
        if not super().__eq__(other):
            return False
        if (other.peripherals is not None) and (self._peripherals is not None):
            if other.peripherals != self._peripherals:
                return False
        return True

    def __str__(self) -> str:
        # TODO consider something more sophisticated
        device = f"{self._name}\n"
        if self._peripherals:
            for peripheral in self._peripherals:
                for substr in str(peripheral).split('\n'):
                    device += f"    {substr}\n"
        return device

    @property
    def peripherals(self) -> List[Peripheral]:
        return self._peripherals
