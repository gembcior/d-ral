"""
D-RAL - Device Register Access Layer
https://github.com/gembcior/d-ral

MIT License

Copyright (c) 2023 Gembcior

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This is an auto generated file. Do not modify!
"""


class Field:
    def __init__(self, name: str, position: int, width: int) -> None:
        self._name = name
        self._position = position
        self._width = width
        self._mask = (1 << width) - 1
        self._value = 0

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def position(self) -> int:
        return self._position

    @property
    def mask(self) -> int:
        return self._mask

    @property
    def width(self) -> int:
        return self._width

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = value & self._mask


class Register:
    def __init__(self, name: str, address: int) -> None:
        self._name = name
        self._address = address
        self._value = 0
        self._fields = self._get_all_fields()
        self._index = 0

    def _get_all_fields(self) -> tuple[Field]:
        fields = list(filter(lambda x: isinstance(x, Field), self.__dict__.values()))
        sorted_fields = sorted(fields, key=lambda x: x.position)
        return tuple(sorted_fields)

    def __setitem__(self, key: int, value: int) -> None:
        self._fields[key].value = value

    def __getitem__(self, key: int) -> Field:
        return self._fields[key]

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._fields):
            item = self._fields[self._index]
            self._index += 1
            return item
        else:
            self._index = 0
            raise StopIteration

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> int:
        return self._address

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        for _, field in self.__dict__.items():
            if isinstance(field, Field):
                field.value = (value >> field.position) & field.mask
        self._value = value


class Peripheral:
    def __init__(self, name: str, address: int) -> None:
        self._name = name
        self._address = address
        self._registers = self._get_all_registers()
        self._index = 0

    def _get_all_registers(self) -> tuple[Register]:
        registers = list(filter(lambda x: isinstance(x, Register), self.__dict__.values()))
        sorted_registers = sorted(registers, key=lambda x: x.address)
        return tuple(sorted_registers)

    def __setitem__(self, key: int, value: int) -> None:
        self._registers[key].value = value

    def __getitem__(self, key: int) -> Register:
        return self._registers[key]

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._registers):
            item = self._registers[self._index]
            self._index += 1
            return item
        else:
            self._index = 0
            raise StopIteration

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> int:
        return self._address


class DralDevice:
    def __init__(self) -> None:
        self._index = 0
        self._peripherals = self._get_all_peripherals()

    def _get_all_peripherals(self) -> tuple[Peripheral]:
        peripheral = list(filter(lambda x: isinstance(x, Peripheral), self.__dict__.values()))
        sorted_peripheral = sorted(peripheral, key=lambda x: x.address)
        return tuple(sorted_peripheral)

    def __getitem__(self, key: int) -> Peripheral:
        return self._peripherals[key]

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < len(self._peripherals):
            item = self._peripherals[self._index]
            self._index += 1
            return item
        else:
            raise StopIteration
