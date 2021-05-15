from abc import ABC, abstractmethod
import importlib.resources as resources
import re


class DralObject(ABC):
    def __init__(self, root):
        super().__init__()
        self._root = root
        self._children = []
        self._dral_prefix = r"\[dral\]"
        self._dral_sufix = r"\[#dral\]"
        self._dral_pattern = re.compile(self._dral_prefix + "(.*?)" + self._dral_sufix, flags=(re.MULTILINE | re.DOTALL))
        self._template = None
        self._name = None
        self.name = self._root["name"]

    def _get_template(self, namespace, name):
        with resources.path("dral.templates.%s" % namespace, name) as template:
            return template

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
        return "".join(content)

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
        for line in string.splitlines(True):
            for pattern in re.findall(self._dral_pattern, line):
                substitution = self._get_pattern_substitution(pattern)
                if substitution is not None:
                    pattern = "%s%s%s" % (self._dral_prefix, pattern, self._dral_sufix)
                    line = re.sub(pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))
            content.append(line)
        return "".join(content)

    def _parse_template(self, template):
        content = []
        with open(template, "r") as f:
            for line in f.readlines():
                for pattern in re.findall(self._dral_pattern, line):
                    substitution = self._get_pattern_substitution(pattern)
                    if substitution is not None:
                        pattern = "%s%s%s" % (self._dral_prefix, pattern, self._dral_sufix)
                        line = re.sub(pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))
                content.append(line)
        return "".join(content)

    def _get_string(self):
        content = self._parse_template(self._template)
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
    def __init__(self, root):
        super().__init__(root)

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "device":
            if pattern[1] == "name":
                substitution = "%s" % self._root["name"]
        return substitution

    def parse(self):
        for item in self._root["peripherals"]:
            peripheral = DralPeripheral(item)
            self._add_children(peripheral)

        content = []
        for child in self._children:
            string = self._parse_string(child.parse())
            content.append({"name": child.name, "content": "".join(string)})
        return content


class DralPeripheral(DralObject):
    def __init__(self, root):
        super().__init__(root)
        self._template = self._get_template("peripheral", "default.dral")

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "peripheral":
            if pattern[1] == "name":
                substitution = "%s" % self._root["name"]
            elif pattern[1] == "address":
                substitution = "0x%08X" % self._root["baseAddress"]
            elif pattern[1] == "registers":
                substitution = self._get_children_content()
                substitution = ("  ".join(("\n" + substitution).splitlines(True))).lstrip("\n")
        return substitution

    def parse(self):
        for item in self._root["registers"]["register"]:
            register = DralRegister(item)
            self._add_children(register)
        return self._get_string()


class DralRegister(DralObject):
    def __init__(self, root):
        super().__init__(root)
        self._template = self._get_template("register", "default.dral")

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "register":
            if pattern[1] == "name":
                substitution = "%s" % self._root["name"]
            elif pattern[1] == "offset":
                substitution = "0x%04X" % self._root["addressOffset"]
            elif pattern[1] == "fields":
                substitution = self._get_children_content()
                substitution = ("  ".join(("\n" + substitution).splitlines(True))).lstrip("\n")
        return substitution

    def parse(self):
        for item in self._root["fields"]:
            field = DralField(item)
            self._add_children(field)
        return self._get_string()


class DralField(DralObject):
    def __init__(self, root):
        super().__init__(root)
        self._template = self._get_template("field", "default.dral")

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "field":
            if pattern[1] == "name":
                substitution = "%s" % self._root["name"]
            elif pattern[1] == "position":
                substitution = "%2d" % self._root["bitOffset"]
            elif pattern[1] == "mask":
                substitution = "0x%08X" % ((1 << self._root["bitWidth"]) - 1)
        return substitution

    def parse(self):
        return self._get_string()
