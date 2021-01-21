class Field:
    def __init__(self):
        self._name = None
        self._position = None
        self._mask = None
        self._policy = None

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

    @property
    def info(self):
        info = ""
        info += "name: %10s | position: %4d | mask: 0x%08X | policy: %4s\n" % (self._name, self._position, self._mask, self._policy)
        return info
