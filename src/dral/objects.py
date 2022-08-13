from abc import ABC, abstractmethod
import re
import sys
from typing import List, Union, overload

from rich.console import Console

from .types import Device, Field, Peripheral, Register, RegisterBank
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


    # TODO refactor register banks support
    def _find_register_banks(self, registers):
        def get_symmetric_difference(str1, str2):
            from difflib import Differ
            differ = Differ()
            output = []
            for item in list(differ.compare(str1, str2)):
                if "+" in item:
                    output.append(item.replace("+", "").strip())
                elif "-" in item:
                    output.append(item.replace("-", "").strip())
            return output

        def is_list_of_digits(digits):
            for item in digits:
                if not item.isdigit():
                    return False
            return True

        def only_one_pos(s1, s2):
            ok = False
            if len(s1) != len(s2):
                return False
            for c1, c2 in zip(s1, s2):
                if c1 != c2:
                    if ok:
                        return False
                    else:
                        ok = True
            return ok

        def compare(item1, item2):
            fields1 = item1.fields
            fields2 = item2.fields
            diff = [i for i in fields1 + fields2 if i not in fields1 or i not in fields2]
            if len(diff) == 0:
                if item1.name != item2.name:
                    diff = get_symmetric_difference(item1.name, item2.name)
                    if is_list_of_digits(diff):
                        return True
                    else:
                        # TODO
                        if only_one_pos(item1.name, item2.name):
                            return True
                        return False
                else:
                    return True
            return False

        banks = []
        registers_copy = registers.copy()
        for reg in registers:
            same = []
            for item in registers_copy:
                if compare(reg, item):
                    same.append(item)
            if len(same) > 1:
                banks.append(same)
                for item in same:
                    registers_copy.remove(item)
        return banks

    def _get_register_banks_offsets(self, registers):
        offsets = []
        for item in registers:
            offsets.append(item.offset)
        diff = [offsets[i+1] - offsets[i] for i in range(len(offsets) - 1)]
        if len(set(diff)) != 1:
            console = Console()
            console.print(f"[red]ERROR: Register banks offset not consistent: {offsets}")
            console.print("Registers dump:")
            console.print(registers)
            sys.exit()
        return min(offsets), diff[0]

    def _get_register_bank_name(self, bank):
        from difflib import SequenceMatcher
        differ = SequenceMatcher(None, bank[0].name, bank[1].name)
        replace = differ.get_opcodes()[1]
        if replace[0] == "replace":
            position = replace[1]
            name = bank[0].name
            name = name[:position] + "x" + name[position+1:]
            return name
        elif replace[0] == "equal":
            name = bank[0].name
            if (len(name) - 1) == len(name[replace[1]:replace[2]]):
                if replace[1] > 0:
                    name = "x" + name[replace[1]:replace[2]]
                else:
                    name = name[replace[1]:replace[2]] + "x"
                return name
        console = Console()
        console.print(f"[red]ERROR: Wrong register bank name {bank[0].name}")
        sys.exit()

    def _merge_register_banks(self, registers):
        register_banks = []
        for bank in registers:
            first_offset, bank_offset = self._get_register_banks_offsets(bank)
            name = self._get_register_bank_name(bank)
            reg = RegisterBank(
                    name = name,
                    description = bank[0].description,
                    offset = first_offset,
                    size = bank[0].size,
                    access = bank[0].access,
                    reset_value = bank[0].reset_value,
                    bank_offset = bank_offset,
                    fields = bank[0].fields)
            register_banks.append(reg)
        return register_banks

    def _get_register_banks(self, registers):
        register_banks = []
        banks = self._find_register_banks(registers)
        if banks:
            register_banks = self._merge_register_banks(banks)
        return register_banks

    def parse(self):
        if "registers" not in self._exclude:
            for item in self._root.registers:
                register = DralRegister(item, self._template, exclude=self._exclude)
                self._add_children("registers", register)
        if "banks" not in self._exclude:
            for item in self._get_register_banks(self._root.registers):
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
    def __init__(self, root: RegisterBank, template: str, exclude: List[str] = []):
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
