from abc import ABC, abstractmethod
import re
from typing import List, Union, overload

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

    def _apply_modifier(self, string, modifier):
        if modifier == "uppercase":
            string = string.upper()
        elif modifier == "lowercase":
            string = string.lower()
        elif modifier == "capitalize":
            string = string.capitalize()
        return string

    def _get_children_content(self, _type: str, variant: str = "default"):
        content = []
        try:
            for item in self._children[_type][variant]:
                content.append(item.parse())
        except KeyError:
            # Raise an exception
            # Key not supported
            # Exit or just warrning
            pass
        return content

    def _get_pattern_substitution(self, pattern):
        modifier = pattern.split("%")
        pattern = modifier[0].split(".")
        if len(modifier) > 1:
            modifier = modifier[1]
        else:
            modifier = None
        substitution = self._get_substitution(pattern)
        if modifier is not None and substitution is not None:
            substitution = self._apply_modifier(substitution, modifier)
        return substitution

    def _parse_string(self, string):
        content = []
        for line in string:
            for pattern in re.findall(self._dral_pattern, line):
                leading_spaces = len(line) - len(line.lstrip(" "))
                leading_spaces = " " * leading_spaces
                substitution = self._get_pattern_substitution(pattern)
                if substitution is not None:
                    pattern = "%s%s%s" % (self._dral_prefix, pattern, self._dral_sufix)
                    if type(substitution) is list:
                        substitution = (leading_spaces.join(substitution)).strip("\n")
                    line = re.sub(pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))
            content.append(line)
        return content

    def _parse_template(self, template):
        content = []
        with open(template, "r") as f:
            for line in f.readlines():
                for pattern in re.findall(self._dral_pattern, line):
                    leading_spaces = len(line) - len(line.lstrip(" "))
                    leading_spaces = " " * leading_spaces
                    substitution = self._get_pattern_substitution(pattern)
                    if substitution is not None:
                        pattern = "%s%s%s" % (self._dral_prefix, pattern, self._dral_sufix)
                        if type(substitution) is list:
                            substitution = (leading_spaces.join(substitution)).strip("\n")
                        line = re.sub(pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))
                content.append(line)
        return content

    def _get_string(self):
        template = Utils.get_template(self._template, self._template_file)
        content = self._parse_template(template)
        content = self._parse_string(content)
        return content

    def _add_children(self, _type: str, element: 'DralObject', variant: str = "default"):
        try:
            self._children[_type][variant].append(element)
        except KeyError:
            self._children.update({_type: {variant: [element]}})

    def _get_substitution(self, pattern: str) -> Union[None, str]:
        substitution = None
        if str(self) == pattern[0]:
            if pattern[1] == "name":
                substitution = "%s" % self._root.name
            elif pattern[1] == "description":
                substitution = "%s" % self._root.description
        return substitution

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value.strip()

    @abstractmethod
    def parse(self):
        pass


class DralDevice(DralObject):
    def __init__(self, root: Device, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude)

    def __str__(self) -> str:
        return "device"

    def parse(self):
        if "peripherals" not in self._exclude:
            for item in self._root.peripherals:
                peripheral = DralPeripheral(item, self._template, exclude=self._exclude)
                self._add_children("peripherals", peripheral)

        content = []
        for child in self._children["peripherals"]["default"]:
            string = self._parse_string(child.parse().splitlines(True))
            content.append({"name": child.name, "content": "".join(string)})
        return content


class DralPeripheral(DralObject):
    def __init__(self, root: Peripheral, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude)
        self._template_file = "peripheral.dral"

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

    def parse(self):
        if "registers" not in self._exclude:
            for item in self._root.registers:
                register = DralRegister(item, self._template, exclude=self._exclude)
                self._add_children("registers", register)
        if "banks" not in self._exclude:
            for item in self._root.banks:
                register = DralBank(item, self._template, exclude=self._exclude)
                self._add_children("banks", register)
        content = "".join(self._get_string())
        return content


class DralRegister(DralObject):
    def __init__(self, root: Register, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude)
        self._template_file = "register.dral"

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
                elif pattern[1] == "resetValue":
                    substitution = "0x%08X" % self._root.reset_value
                elif pattern[1] in ["fields"]:
                    if len(pattern) > 2:
                        substitution = self._get_children_content(pattern[1], pattern[2])
                    else:
                        substitution = self._get_children_content(pattern[1])
        return substitution

    def parse(self):
        if "fields" not in self._exclude:
            for item in self._root.fields:
                field = DralField(item, self._template, exclude=self._exclude)
                self._add_children("fields", field)
        content = "".join(self._get_string())
        return content


class DralBank(DralRegister):
    def __init__(self, root: Bank, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude=exclude)
        self._template_file = "bank.dral"

    def __str__(self) -> str:
        return "bank"

    def _get_substitution(self, pattern):
        substitution = super()._get_substitution(pattern)
        if substitution is None:
            if str(self) == pattern[0]:
                if pattern[1] == "bankOffset":
                    substitution = "0x%04X" % self._root.bank_offset
        return substitution

    def parse(self):
        if "fields" not in self._exclude:
            for item in self._root.fields:
                field = DralBankField(item, self._template, exclude=self._exclude)
                self._add_children("fields", field)
        content = "".join(self._get_string())
        return content


class DralField(DralObject):
    def __init__(self, root: Field, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude)
        self._template_file = "field.dral"

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

    def parse(self):
        content = "".join(self._get_string())
        return content


class DralBankField(DralField):
    def __init__(self, root: Field, template: str, exclude: List[str] = []):
        super().__init__(root, template, exclude)
        self._template_file = "bank.field.dral"
