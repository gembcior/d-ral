from abc import ABC, abstractmethod
from pathlib import Path
import importlib.resources as resources
import re


class DralObject(ABC):
    def __init__(self, root, exclude=[]):
        super().__init__()
        self._root = root
        self._exclude = exclude
        self._children = []
        self._dral_prefix = r"\[dral\]"
        self._dral_sufix = r"\[#dral\]"
        self._dral_pattern = re.compile(self._dral_prefix + "(.*?)" + self._dral_sufix, flags=(re.MULTILINE | re.DOTALL))
        self._template_file = None
        self._name = None
        self.name = self._root["name"]

    def _get_template(self, namespace, name):
        with resources.path("dral.templates.%s" % namespace, name) as template:
            return Path(template)

    def _apply_modifier(self, string, modifier):
        if modifier == "uppercase":
            string = string.upper()
        elif modifier == "lowercase":
            string = string.lower()
        elif modifier == "capitalize":
            string = string.capitalize()
        return string

    def _get_children_content(self):
        content = []
        for item in self._children:
            content.append(item.parse())
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
                        substitution = (leading_spaces.join(substitution)).lstrip("\n")
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
                            substitution = (leading_spaces.join(substitution)).lstrip("\n")
                        line = re.sub(pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))
                content.append(line)
        return content

    def _get_string(self):
        content = self._parse_template(self._template_file)
        content = self._parse_string(content)
        return content

    def _add_children(self, element):
        self._children.append(element)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip()

    @abstractmethod
    def _get_substitution(self, pattern):
        pass

    @abstractmethod
    def parse(self):
        pass


class DralDevice(DralObject):
    def __init__(self, root, template="default", exclude=[]):
        super().__init__(root, exclude)
        self._template = template

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "device":
            if pattern[1] == "name":
                substitution = "%s" % self._root["name"]
        return substitution

    def parse(self):
        if "peripherals" not in self._exclude:
            for item in self._root["peripherals"]:
                peripheral = DralPeripheral(item, template=self._template, exclude=self._exclude)
                self._add_children(peripheral)

        content = []
        for child in self._children:
            string = self._parse_string(child.parse().splitlines(True))
            content.append({"name": child.name, "content": "".join(string)})
        return content


class DralPeripheral(DralObject):
    def __init__(self, root, template="default", exclude=[]):
        super().__init__(root, exclude)
        self._template = template
        self._template_file = self._get_template(template, "peripheral.dral")

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "peripheral":
            if pattern[1] == "name":
                substitution = "%s" % self._root["name"]
            elif pattern[1] == "address":
                substitution = "0x%08X" % self._root["baseAddress"]
            elif pattern[1] == "registers":
                substitution = self._get_children_content()
        return substitution


    # TODO refactor register banks support
    def _find_register_banks(self, registers):
        def compare(item1, item2):
            diff = [i for i in item1 + item2 if i not in item1 or i not in item2]
            return len(diff) == 0
        banks = []
        registers_copy = registers.copy()
        for reg in registers:
            same = []
            for item in registers_copy:
                if compare(reg["fields"], item["fields"]):
                    same.append(item)
            if len(same) > 1:
                banks.append(same)
                for item in same:
                    registers_copy.remove(item)
        return banks

    def _get_register_banks_offsets(self, registers):
        offsets = []
        for item in registers:
            offsets.append(item["addressOffset"])
        return offsets

    def _get_bank_offset(self, offsets):
        diff = [offsets[i+1] - offsets[i] for i in range(len(offsets) - 1)]
        if len(set(diff)) == 1:
            return diff[0]
        else:
            # TODO implement better error handling
            print(f"ERROR: Register banks offset differ: {diff}")

    def _get_first_bank_offset(self, offsets):
        return min(offsets)

    def _merge_register_banks(self, registers):
        register_banks = []
        for bank in registers:
            offsets = self._get_register_banks_offsets(bank)
            first_offset = self._get_first_bank_offset(offsets)
            bank_offset = self._get_bank_offset(offsets)
            bank_name_pattern = re.compile(r"[\d]")
            reg = {
                'name': re.sub(bank_name_pattern, "x", bank[0]["name"]),
                'displayName': re.sub(bank_name_pattern, "x", bank[0]["displayName"]),
                'description': bank[0]["description"],
                'addressOffset': first_offset,
                'size': bank[0]["size"],
                'resetValue': bank[0]["resetValue"],
                'fields': bank[0]["fields"],
                'bankOffset': bank_offset
            }
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
            for item in self._root["registers"]["register"]:
                register = DralRegister(item, template=self._template, exclude=self._exclude)
                self._add_children(register)
        if "banks" not in self._exclude:
            for item in self._get_register_banks(self._root["registers"]["register"]):
                register = DralRegisterBank(item, template=self._template, exclude=self._exclude)
                self._add_children(register)
        content = "".join(self._get_string())
        return content


class DralRegister(DralObject):
    def __init__(self, root, template="default", exclude=[]):
        super().__init__(root, exclude)
        self._template = template
        self._template_file = self._get_template(template, "register.dral")

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "register":
            if pattern[1] == "name":
                substitution = "%s" % self._root["name"]
            elif pattern[1] == "offset":
                substitution = "0x%04X" % self._root["addressOffset"]
            elif pattern[1] == "fields":
                substitution = self._get_children_content()
            elif pattern[1] == "description":
                substitution = "%s" % self._root["description"]
            elif pattern[1] == "access":
                substitution = "%s" % self._root["access"]
            elif pattern[1] == "resetValue":
                substitution = "0x%08X" % self._root["resetValue"]
        return substitution

    def parse(self):
        if "fields" not in self._exclude:
            for item in self._root["fields"]:
                field = DralField(item, template=self._template, exclude=self._exclude)
                self._add_children(field)
        content = "".join(self._get_string())
        return content


class DralRegisterBank(DralRegister):
    def __init__(self, root, template="default", exclude=[]):
        super().__init__(root, exclude)
        self._template = template
        self._template_file = self._get_template(template, "bank.dral")

    def _get_substitution(self, pattern):
        substitution = super()._get_substitution(pattern)
        if pattern[0] == "register":
            if pattern[1] == "bankOffset":
                substitution = "0x%04X" % self._root["bankOffset"]
        return substitution


class DralField(DralObject):
    def __init__(self, root, template="default", exclude=[]):
        super().__init__(root, exclude)
        self._template_file = self._get_template(template, "field.dral")

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "field":
            if pattern[1] == "name":
                substitution = "%s" % self._root["name"]
            elif pattern[1] == "position":
                substitution = "%2d" % self._root["bitOffset"]
            elif pattern[1] == "mask":
                substitution = "0x%08X" % ((1 << self._root["bitWidth"]) - 1)
            elif pattern[1] == "width":
                substitution = "%d" % self._root["bitWidth"]
            elif pattern[1] == "description":
                substitution = "%s" % self._root["description"]
        return substitution

    def parse(self):
        content = "".join(self._get_string())
        return content
