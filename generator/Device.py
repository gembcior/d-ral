class Device:
    def __init__(self):
        self._brand = None
        self._family = None
        self._chip = None
        self._peripherals = {}

    @property
    def brand(self):
        return self._brand

    @brand.setter
    def brand(self, value):
        self._brand = value.strip()

    @property
    def family(self):
        return self._family

    @family.setter
    def family(self, value):
        self._family = value.strip()

    @property
    def chip(self):
        return self._chip

    @chip.setter
    def chip(self, value):
        self._chip = value.strip()

    @property
    def peripherals(self):
        return self._peripherals

    @peripherals.setter
    def peripherals(self, value):
        self._peripherals = value
