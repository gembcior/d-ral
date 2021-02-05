from DralObject import DralObject


class Peripheral(DralObject):
    def __init__(self):
        super().__init__()
        self._name = None
        self._type = None
        self._address = None
        self._registers = None
        self._template = "peripheral/normal/file.dral"

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

    def _get_registers_content(self, kind=None):
        content = []
        for reg in self._registers:
            if kind == "declaration":
                content.append(reg.get_declaration_string())
                content.append("\n")
            elif kind == "instance":
                content.append(reg.get_instance_string())
            else:
                content.append(reg.get_string())
                content.append("\n")
        return "".join(content)

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "peripheral":
            if pattern[1] == "name":
                substitution = self._name
            elif pattern[1] == "address":
                substitution = "0x%08X" % self._address
            elif pattern[1] == "registers":
                if len(pattern) > 2:
                    if pattern[2] == "declaration":
                        substitution = self._get_registers_content(pattern[2])
                    elif pattern[2] == "instance":
                        substitution = self._get_registers_content(pattern[2])
                        substitution = ("  ".join(("\n" + substitution).splitlines(True))).lstrip("\n")
                else:
                    substitution = self._get_registers_content()
        return substitution

