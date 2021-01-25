from Object import Object
import os
import re


class Peripheral(Object):
    def __init__(self):
        self._name = None
        self._type = None
        self._address = None
        self._registers = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip()

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value.strip()

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

    @property
    def registers(self):
        return self._registers

    @registers.setter
    def registers(self, value):
        self._registers = value

    def _get_pattern_substitution(self, pattern):
        substitution = "ERROR"
        pattern = pattern.split(".")
        if pattern[0] == "peripheral":
            if pattern[1] == "name":
                substitution = self._name
            elif pattern[1] == "address":
                substitution = "0x%08X" % self._address
            elif pattern[1] == "registers":
                content = []
                for reg in self._registers:
                    content.append("".join(reg.generate()))
                    content.append("\n")
                substitution = "".join(content)
        if len(pattern) > 2:
            substitution = self._apply_modifier(substitution, pattern[2])
        return substitution

    def generate(self):
        content = []
        path = os.path.dirname(os.path.realpath(__file__))
        peripheral_file_template = os.path.join(path, "..", "templates", "peripheral_normal.dral")
        dral_pattern = re.compile('\[dral\](.*?)\[#dral\]')
        with open(peripheral_file_template,"r") as template:
            for line in template.readlines():
                for pattern in re.findall(dral_pattern, line):
                    substitution = self._get_pattern_substitution(pattern)
                    line = re.sub("\[dral\]%s\[#dral\]" % pattern, substitution, line)
                content.append(line)
        return content


class PeripheralCollection(Peripheral):
    def __init__(self):
        super(Peripheral, self).__init__()
