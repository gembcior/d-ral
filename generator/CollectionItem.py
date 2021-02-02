from DralObject import DralObject


class CollectionItem(DralObject):
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

