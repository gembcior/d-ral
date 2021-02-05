from DralObject import DralObject
from Peripheral import Peripheral


class Collection(Peripheral):
    def __init__(self):
        super().__init__()
        self._instances = None
        self._template = "peripheral/collection/file.dral"

    @property
    def instances(self):
        return self._instances

    @instances.setter
    def instances(self, value):
        self._instances = value

    def _get_instances_content(self):
        content = []
        for item in self._instances:
            content.append(item.get_string())
        return "".join(content)

    def _get_substitution(self, pattern):
        substitution = None
        substitution = super()._get_substitution(pattern)
        if substitution is None:
            if pattern[0] == "collection":
                if pattern[1] == "instances":
                    substitution = self._get_instances_content()
        return substitution


class CollectionInstance(DralObject):
    def __init__(self):
        super().__init__()
        self._name = None
        self._address = None
        self._template = "peripheral/collection/instance.dral"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip()

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "collection":
            if pattern[1] == "name":
                substitution = self._name
            elif pattern[1] == "address":
                substitution = "0x%08X" % self._address
        return substitution
