from DralObject import DralObject


class Device(DralObject):
    def __init__(self):
        super().__init__()
        self._brand = None
        self._family = None
        self._chip = None
        self._model = None
        self._peripherals = []

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
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def peripherals(self):
        return self._peripherals

    @peripherals.setter
    def peripherals(self, value):
        self._peripherals = value

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "device":
            if pattern[1] == "brand":
                substitution = self._brand
            elif pattern[1] == "family":
                substitution = self._family
            elif pattern[1] == "chip":
                substitution = self._chip
            elif pattern[1] == "model":
                substitution = self._model.name
        return substitution

    def _get_component_content(self, component):
        content = []
        for item in component:
            string = self._generate_from_string(item.get_string())
            content.append({"name": item.name, "content": "".join(string)})
        return content

    def generate(self):
        content = []
        content += self._get_component_content(self._peripherals)
        content += self._get_component_content([self._model])
        return content
