from Object import Object


class Peripheral(Object):
    def __init__(self):
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

    def _get_pattern_substitution(self, pattern):
        substitution = None
        pattern = pattern.split(".")
        if pattern[0] == "peripheral":
            if pattern[1] == "name":
                substitution = self._name
            elif pattern[1] == "address":
                substitution = "0x%08X" % self._address
            elif pattern[1] == "registers":
                content = []
                for reg in self._registers:
                    content.append(reg.get_string())
                    content.append("\n")
                substitution = "".join(content)
            if len(pattern) > 2:
                substitution = self._apply_modifier(substitution, pattern[2])
        return substitution


class PeripheralCollection(Peripheral):
    def __init__(self):
        super().__init__()
        self._collection = None
        self._template = "peripheral/collection/file.dral"

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, value):
        self._collection = value

    def _get_pattern_substitution(self, pattern):
        substitution = None
        pattern = pattern.split(".")
        if pattern[0] == "peripheral":
            if pattern[1] == "name":
                substitution = self._name
            elif pattern[1] == "address":
                substitution = "0x%08X" % self._address
            elif pattern[1] == "registers":
                if pattern[2] == "declaration":
                    content = []
                    for reg in self._registers:
                        content.append(reg.get_declaration_string())
                        content.append("\n")
                    substitution = "".join(content)
                elif pattern[2] == "instance":
                    content = []
                    for reg in self._registers:
                        content.append(reg.get_instance_string())
                    substitution = "".join(content)
                    substitution = ("  ".join(("\n" + substitution).splitlines(True))).lstrip("\n")
            elif pattern[1] == "collection":
                content = []
                for item in self._collection:
                    content.append(item.get_string())
                substitution = "".join(content)
            if len(pattern) > 2:
                substitution = self._apply_modifier(substitution, pattern[2])
        return substitution

