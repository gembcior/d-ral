import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterator, List, Union

from .types import Bank, Device, Field, Peripheral, Register
from .utils import Utils


class DralPatternInvalid(Exception):
    def __init__(self, *args: Any) -> None:
        super().__init__(args)


class DralObject(ABC):
    def __init__(
        self,
        root: Union[Device, Peripheral, Register, Field],
        template: str = "default",
        exclude: Union[None, List[str]] = None,
    ):
        super().__init__()
        self._children: Dict[str, List[Union[DralPeripheral, DralRegister, DralBank, DralField]]] = {}
        self._dral_prefix = r"\[dral\]"
        self._dral_sufix = r"\[#dral\]"
        self._dral_pattern = re.compile(
            self._dral_prefix + "(.*?)" + self._dral_sufix,
            flags=(re.MULTILINE | re.DOTALL),
        )
        if exclude is None:
            exclude = []
        self._exclude = exclude
        self._name = ""
        self._root = root
        self._template = template
        self._template_file: Dict[str, str] = {}
        self.name = self._root.name

    def _apply_modifier(self, item: Union[str, List[str]], modifier: str) -> Union[str, List[str]]:
        output = item
        if isinstance(item, str):
            output = self._apply_string_modifier(item, modifier)
        elif isinstance(item, list):
            output = self._apply_list_modifier(item, modifier)
        return output

    def _apply_string_modifier(self, string: str, modifier: str) -> str:
        if modifier == "uppercase":
            string = string.upper()
        elif modifier == "lowercase":
            string = string.lower()
        elif modifier == "capitalize":
            string = string.capitalize()
        elif modifier == "strip":
            string = string.strip(" \n\r")
        elif modifier == "LF":
            string = string + "\n"
        return string

    def _apply_list_modifier(self, _list: List[str], modifier: str) -> List[str]:
        if modifier == "LF":
            _list = _list + ["\n"]
        return _list

    def _get_children_content(self, _type: str, variant: str = "default") -> List[str]:
        content: List[str] = []
        try:
            for item in self._children[_type]:
                content = content + item.parse(variant)
        except KeyError:
            # Raise an exception
            # Key not supported
            # Exit or just warrning
            pass
        return content

    def _get_pattern_substitution(self, pattern: str) -> Union[None, str, List[str]]:
        split_pattern = pattern.split("%")
        base = split_pattern[0].split(".")
        modifier = split_pattern[1:]
        substitution = self._get_substitution(base)
        if substitution is not None:
            for item in modifier:
                substitution = self._apply_modifier(substitution, item)
            return substitution
        return None

    def _find_all_dral_pattern(self, string: str) -> Iterator[Any]:
        return re.finditer(self._dral_pattern, string)

    def _replace_line(self, line: str) -> Union[str, None]:
        dral_matches = self._find_all_dral_pattern(line)
        if dral_matches:  # type: ignore[truthy-bool]
            for match in dral_matches:
                pattern = match.group(1)
                position = match.start()
                leading_spaces = " " * position
                substitution = self._get_pattern_substitution(pattern)
                if substitution is not None:
                    pattern = f"{self._dral_prefix}{pattern}{self._dral_sufix}"
                    if isinstance(substitution, list):
                        substitution = (leading_spaces.join(substitution)).strip("\n")
                    line = re.sub(pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))  # type: ignore[arg-type]
            return line
        return None

    def _parse_string(self, string: List[str]) -> List[str]:
        content: List[str] = []
        for line in string:
            new_line = self._replace_line(line)
            if new_line is not None:
                content.append(new_line)
            else:
                content.append(line)
        new_content: List[str] = []
        for item in content:
            new_content = new_content + item.splitlines(True)
        return new_content

    def _parse_template(self, template: Path) -> List[str]:
        with open(template, "r", encoding="UTF-8") as file:
            template_content = file.readlines()
        return self._parse_string(template_content)

    def _get_string(self, variant: str) -> List[str]:
        template = Utils.get_template(self._template, self._template_file[variant])
        content = self._parse_template(template)
        return content

    def _add_children(self, _type: str, element: Union["DralPeripheral", "DralRegister", "DralField"]) -> None:
        try:
            self._children[_type].append(element)
        except KeyError:
            self._children.update({_type: [element]})

    def _get_substitution(self, pattern: List[str]) -> Union[None, str, List[str]]:
        substitution = None
        if str(self) == pattern[0]:
            if pattern[1] == "name":
                substitution = f"{self._root.name}"
            elif pattern[1] == "description":
                # TODO strip, remove new lines etc.
                substitution = ""
        return substitution

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value.strip()

    @abstractmethod
    def parse(self, variant: str = "default") -> List[str]:
        pass


class DralDevice(DralObject):
    def __init__(self, root: Device, template: str, exclude: Union[None, List[str]] = None):
        super().__init__(root, template, exclude)

    def __str__(self) -> str:
        return "device"

    def parse(self, variant: str = "default") -> List[Dict[str, str]]:  # type: ignore[override]
        if "peripherals" not in self._exclude:
            for item in self._root.peripherals:  # type: ignore[union-attr]
                peripheral = DralPeripheral(item, self._template, exclude=self._exclude)
                self._add_children("peripherals", peripheral)

        content = []
        for child in self._children["peripherals"]:
            string = self._parse_string(child.parse(variant))
            content.append({"name": child.name, "content": "".join(string)})
        return content


class DralPeripheral(DralObject):
    def __init__(self, root: Peripheral, template: str, exclude: Union[None, List[str]] = None):
        super().__init__(root, template, exclude)
        self._template_file = {"default": "peripheral.dral"}

    def __str__(self) -> str:
        return "peripheral"

    def _get_substitution(self, pattern: List[str]) -> Union[None, str, List[str]]:
        substitution = super()._get_substitution(pattern)
        if substitution is None:
            if str(self) == pattern[0]:
                if pattern[1] == "address":
                    substitution = f"0x{self._root.address:08X}"  # type: ignore[union-attr]
                elif pattern[1] in ["registers", "banks"]:
                    if len(pattern) > 2:
                        substitution = self._get_children_content(pattern[1], pattern[2])
                    else:
                        substitution = self._get_children_content(pattern[1])
        return substitution

    def parse(self, variant: str = "default") -> List[str]:
        if "registers" not in self._exclude:
            for item in self._root.registers:  # type: ignore[union-attr]
                register = DralRegister(item, self._template, exclude=self._exclude)
                self._add_children("registers", register)
        if "banks" not in self._exclude:
            for item in self._root.banks:  # type: ignore[union-attr]
                register = DralBank(item, self._template, exclude=self._exclude)
                self._add_children("banks", register)
        content = self._get_string(variant)
        return content


class DralRegister(DralObject):
    def __init__(self, root: Register, template: str, exclude: Union[None, List[str]] = None):
        super().__init__(root, template, exclude)
        self._template_file = {
            "default": "register.dral",
            "simple": "register.simple.dral",
        }

    def __str__(self) -> str:
        return "register"

    def _get_substitution(self, pattern: List[str]) -> Union[None, str, List[str]]:
        substitution = super()._get_substitution(pattern)
        if substitution is None:
            if str(self) == pattern[0]:
                if pattern[1] == "offset":
                    substitution = f"0x{self._root.offset:04X}"  # type: ignore[union-attr]
                elif pattern[1] == "size":
                    substitution = f"{self._root.size}"  # type: ignore[union-attr]
                elif pattern[1] == "access":
                    substitution = str(self._root.access)  # type: ignore[union-attr]
                elif pattern[1] == "reset_value":
                    substitution = f"0x{self._root.reset_value:08X}"  # type: ignore[union-attr]
                elif pattern[1] in ["fields"]:
                    if len(pattern) > 2:
                        substitution = self._get_children_content(pattern[1], pattern[2])
                    else:
                        substitution = self._get_children_content(pattern[1])
        return substitution

    def parse(self, variant: str = "default") -> List[str]:
        if "fields" not in self._exclude:
            for item in self._root.fields:  # type: ignore[union-attr]
                field = DralField(item, self._template, exclude=self._exclude)
                self._add_children("fields", field)
        content = self._get_string(variant)
        return content


class DralBank(DralRegister):
    def __init__(self, root: Bank, template: str, exclude: Union[None, List[str]] = None):
        super().__init__(root, template, exclude=exclude)
        self._template_file = {"default": "bank.dral"}

    def __str__(self) -> str:
        return "bank"

    def _get_substitution(self, pattern: List[str]) -> Union[None, str, List[str]]:
        substitution = super()._get_substitution(pattern)
        if substitution is None:
            if str(self) == pattern[0]:
                if pattern[1] == "bankOffset":
                    substitution = f"0x{self._root.bank_offset:04X}"  # type: ignore[union-attr]
        return substitution

    def parse(self, variant: str = "default") -> List[str]:
        if "fields" not in self._exclude:
            for item in self._root.fields:  # type: ignore[union-attr]
                field = DralBankField(item, self._template, exclude=self._exclude)
                self._add_children("fields", field)
        content = self._get_string(variant)
        return content


class DralField(DralObject):
    def __init__(self, root: Field, template: str, exclude: Union[None, List[str]] = None):
        super().__init__(root, template, exclude)
        self._template_file = {"default": "field.dral"}

    def __str__(self) -> str:
        return "field"

    def _get_substitution(self, pattern: List[str]) -> Union[None, str, List[str]]:
        substitution = super()._get_substitution(pattern)
        if substitution is None:
            if str(self) == pattern[0]:
                if pattern[1] == "position":
                    substitution = f"{self._root.position}"  # type: ignore[union-attr]
                elif pattern[1] == "mask":
                    substitution = f"0x{self._root.mask:08X}"  # type: ignore[union-attr]
                elif pattern[1] == "width":
                    substitution = f"{self._root.width}"  # type: ignore[union-attr]
        return substitution

    def parse(self, variant: str = "default") -> List[str]:
        content = self._get_string(variant)
        return content


class DralBankField(DralField):
    def __init__(self, root: Field, template: str, exclude: Union[None, List[str]] = None):
        super().__init__(root, template, exclude)
        self._template_file = {"default": "bank.field.dral"}
