from abc import ABC, abstractmethod
import re
from typing import List, Union, overload, Iterator

from .types import Device, Field, Peripheral, Register, Bank
from .utils import Utils


class DralPatternInvalid(Exception):
    def __init__(self, *args):
        super().__init__(args)


class DralObject(ABC):
    @overload
    def __init__(self, root: Device, template: str, exclude: List[str] = []):
        ...
    @overload
    def __init__(self, root: Peripheral, template: str,exclude: List[str] = []):
        ...
    @overload
    def __init__(self, root: Register, template: str, exclude: List[str] = []):
        ...
    @overload
    def __init__(self, root: Field, template: str, exclude: List[str] = []):
        ...
    def __init__(self, root, template="default", exclude=[]):
        super().__init__()
        self._children = {}
        self._dral_prefix = r"\[dral\]"
        self._dral_sufix = r"\[#dral\]"
        self._dral_pattern = re.compile(self._dral_prefix + "(.*?)" + self._dral_sufix, flags=(re.MULTILINE | re.DOTALL))
        self._exclude = exclude
        self._name = None
        self._root = root
        self._template = template
        self._template_file = ""
        self.name = self._root.name

    def _apply_modifier(self, string: Union[str, List], modifier: str):
        if modifier == "uppercase":
            if type(string) is str:
                string = string.upper()
        elif modifier == "lowercase":
            if type(string) is str:
                string = string.lower()
        elif modifier == "capitalize":
            if type(string) is str:
                string = string.capitalize()
        elif modifier == "strip":
            if type(string) is str:
                string = string.strip(" \n\r")
        elif modifier == "LF":
            if type(string) is str:
                string = string + "\n"
            else:
                string = string + ["\n"]
        return string

    def _get_children_content(self, _type: str, variant: str = "default"):
        content = []
        try:
            for item in self._children[_type]:
                content = content + item.parse(variant)
        except KeyError:
            # Raise an exception
            # Key not supported
            # Exit or just warrning
            pass
        return content

    def _get_pattern_substitution(self, pattern):
        modifier = pattern.split("%")
        pattern = modifier[0].split(".")
        substitution = self._get_substitution(pattern)
        if substitution is not None:
            if len(modifier) > 1:
                for item in modifier[1:]:
                    substitution = self._apply_modifier(substitution, item)
        return substitution


    def _find_all_dral_pattern(self, string: str) -> Iterator[re.Match[str]]:
        return re.finditer(self._dral_pattern, string)

    def _replace_line(self, line: str) -> Union[str, None]:
        dral_matches = self._find_all_dral_pattern(line)
        if dral_matches:
            for match in dral_matches:
                pattern = match.group(1)
                position = match.start()
                leading_spaces = " " * position
                substitution = self._get_pattern_substitution(pattern)
                if substitution is not None:
                    pattern = f"{self._dral_prefix}{pattern}{self._dral_sufix}"
                    if type(substitution) is list:
                        substitution = (leading_spaces.join(substitution)).strip("\n")
                    line = re.sub(pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))
            return line
        else:
            return None

    def _parse_string(self, string):
        content = []
        for line in string:
            new_line = self._replace_line(line)
            if new_line is not None:
                content.append(new_line)
            else:
                content.append(line)
        new_content = []
        for item in content:
            new_content = new_content + item.splitlines(True)
        return new_content

    def _parse_template(self, template):
        with open(template, "r") as f:
            template_content = f.readlines()
        return self._parse_string(template_content)

    def _get_string(self, variant):
        template = Utils.get_template(self._template, self._template_file[variant])
        content = self._parse_template(template)
        # content = self._parse_string(content)
        return content

    def _add_children(self, _type: str, element: 'DralObject'):
        try:
            self._children[_type].append(element)
        except KeyError:
            self._children.update({_type: [element]})

    def _get_substitution(self, pattern: str) -> Union[None, str]:
        substitution = None
        if str(self) == pattern[0]:
            if pattern[1] == "name":
                substitution = "%s" % self._root.name
            elif pattern[1] == "description":
                # TODO strip, remove new lines etc.
                # substitution = "%s" % self._root.description
                substitution = ""
        return substitution

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value.strip()

    @abstractmethod
    def parse(self, variant: str="default"):
        pass


class DralDevice(DralObject):
    def __init__(self, root: Device, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude)

    def __str__(self) -> str:
        return "device"

    def parse(self, variant: str="default"):
        if "peripherals" not in self._exclude:
            for item in self._root.peripherals:
                peripheral = DralPeripheral(item, self._template, exclude=self._exclude)
                self._add_children("peripherals", peripheral)

        content = []
        for child in self._children["peripherals"]:
            string = self._parse_string(child.parse(variant))
            content.append({"name": child.name, "content": "".join(string)})
        return content


class DralPeripheral(DralObject):
    def __init__(self, root: Peripheral, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude)
        self._template_file = {"default": "peripheral.dral"}

    def __str__(self) -> str:
        return "peripheral"

    def _get_substitution(self, pattern):
        substitution = super()._get_substitution(pattern)
        if substitution is None:
            if str(self) == pattern[0]:
                if pattern[1] == "address":
                    substitution = "0x%08X" % self._root.address
                elif pattern[1] in ["registers", "banks"]:
                    if len(pattern) > 2:
                        substitution = self._get_children_content(pattern[1], pattern[2])
                    else:
                        substitution = self._get_children_content(pattern[1])
        return substitution

    def parse(self, variant: str="default"):
        if "registers" not in self._exclude:
            for item in self._root.registers:
                register = DralRegister(item, self._template, exclude=self._exclude)
                self._add_children("registers", register)
        if "banks" not in self._exclude:
            for item in self._root.banks:
                register = DralBank(item, self._template, exclude=self._exclude)
                self._add_children("banks", register)
        content = self._get_string(variant)
        return content


class DralRegister(DralObject):
    def __init__(self, root: Register, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude)
        self._template_file = {"default": "register.dral",
                               "simple": "register.simple.dral"}

    def __str__(self) -> str:
        return "register"

    def _get_substitution(self, pattern):
        substitution = super()._get_substitution(pattern)
        if substitution is None:
            if str(self) == pattern[0]:
                if pattern[1] == "offset":
                    substitution = "0x%04X" % self._root.offset
                elif pattern[1] == "size":
                    substitution = "%d" % self._root.size
                elif pattern[1] == "access":
                    substitution = "%s" % self._root.access
                elif pattern[1] == "reset_value":
                    substitution = "0x%08X" % self._root.reset_value
                elif pattern[1] in ["fields"]:
                    if len(pattern) > 2:
                        substitution = self._get_children_content(pattern[1], pattern[2])
                    else:
                        substitution = self._get_children_content(pattern[1])
        return substitution

    def parse(self, variant: str="default"):
        if "fields" not in self._exclude:
            for item in self._root.fields:
                field = DralField(item, self._template, exclude=self._exclude)
                self._add_children("fields", field)
        content = self._get_string(variant)
        return content


class DralBank(DralRegister):
    def __init__(self, root: Bank, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude=exclude)
        self._template_file = {"default": "bank.dral"}

    def __str__(self) -> str:
        return "bank"

    def _get_substitution(self, pattern):
        substitution = super()._get_substitution(pattern)
        if substitution is None:
            if str(self) == pattern[0]:
                if pattern[1] == "bankOffset":
                    substitution = "0x%04X" % self._root.bank_offset
        return substitution

    def parse(self, variant: str="default"):
        if "fields" not in self._exclude:
            for item in self._root.fields:
                field = DralBankField(item, self._template, exclude=self._exclude)
                self._add_children("fields", field)
        content = self._get_string(variant)
        return content


class DralField(DralObject):
    def __init__(self, root: Field, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude)
        self._template_file = {"default": "field.dral"}

    def __str__(self) -> str:
        return "field"

    def _get_substitution(self, pattern):
        substitution = super()._get_substitution(pattern)
        if substitution is None:
            if str(self) == pattern[0]:
                if pattern[1] == "position":
                    substitution = "%d" % self._root.position
                elif pattern[1] == "mask":
                    substitution = "0x%08X" % self._root.mask
                elif pattern[1] == "width":
                    substitution = "%d" % self._root.width
        return substitution

    def parse(self, variant: str="default"):
        content = self._get_string(variant)
        return content


class DralBankField(DralField):
    def __init__(self, root: Field, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude)
        self._template_file = {"default": "bank.field.dral"}
