from Object import Object


class Field(Object):
    def __init__(self):
        self._name = None
        self._position = None
        self._mask = None
        self._policy = None
        self._template = "field/normal.dral"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip()

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def policy(self):
        return self._policy

    @policy.setter
    def policy(self, value):
        self._policy = value

    @property
    def mask(self):
        return self._mask

    @mask.setter
    def mask(self, value):
        self._mask = value

    def _get_pattern_substitution(self, pattern):
        substitution = None
        pattern = pattern.split(".")
        if pattern[0] == "field":
            if pattern[1] == "name":
                substitution = "%-12s" % self._name
            elif pattern[1] == "position":
                substitution = "%2d" % self._position
            elif pattern[1] == "policy":
                substitution = self._get_policy(self._policy)
            elif pattern[1] == "mask":
                substitution = "0x%08X" % self._mask
            if len(pattern) > 2:
                substitution = self._apply_modifier(substitution, pattern[2])
        return substitution

