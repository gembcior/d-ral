class Peripheral:
    def __init__(self):
        self._name = None
        self._address = None
        self._registers = None

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

    @property
    def registers(self):
        return self._registers

    @registers.setter
    def registers(self, value):
        self._registers = value

    @property
    def info(self):
        info = ""
        info += "----PERIPHERAL--------------------------------------------------------------\n"
        info += "%s | address: 0x%08X\n" % (self._name, self._address)
        if self._registers is not None:
            for reg in self._registers:
                info += "    ----REGISTER------------------------------------------------------------\n"
                info += ('    '.join(("\n" + reg.info).splitlines(True))).lstrip("\n")
                info += "\n"
        return info
