class Register:
    def __init__(self):
        self._name = None
        self._offset = None
        self._policy = None
        self._fields = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip()

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def policy(self):
        return self._policy

    @policy.setter
    def policy(self, value):
        self._policy = value

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, value):
        self._fields = value

    @property
    def info(self):
        info = ""
        info += "%s | offset: 0x%04X | policy: %4s\n" % (self._name, self._offset, self._policy)
        info += "    ----FIELDS----------------------------------------------------------\n"

        if self._fields is not None:
            for field in self._fields:
                info += ('    '.join(("\n" + field.info).splitlines(True))).lstrip("\n")
        return info

