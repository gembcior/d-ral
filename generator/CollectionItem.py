from Object import Object


class CollectionItem(Object):
    def __init__(self):
        self._parent = None
        self._name = None
        self._address = None
        self._template = "peripheral/collection/instance.dral"

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value.strip()

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

    def _get_pattern_substitution(self, pattern):
        substitution = None
        pattern = pattern.split(".")
        if pattern[0] == "collection":
            if pattern[1] == "name":
                substitution = self._name
            if pattern[1] == "parent":
                substitution = self._parent
            elif pattern[1] == "address":
                substitution = "0x%08X" % self._address
            if len(pattern) > 2:
                substitution = self._apply_modifier(substitution, pattern[2])
        return substitution

