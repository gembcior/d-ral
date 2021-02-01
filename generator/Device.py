from DeviceItem import DeviceItem
import os
import re


class Device(DeviceItem):
    def __init__(self):
        super().__init__()
        self._brand = None
        self._family = None
        self._chip = None
        self._model = None
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
        dral_pattern = re.compile('\[dral\](.*?)\[#dral\]', flags=(re.MULTILINE | re.DOTALL))
        content = []
        for item in component:
            component_content = []
            for line in item.get_string().splitlines(True):
                for pattern in re.findall(dral_pattern, line):
                    substitution = self._get_pattern_substitution(pattern)
                    if substitution is not None:
                        line = re.sub("\[dral\]%s\[#dral\]" % pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))
                component_content.append(line)
            content.append({"name": item.name, "content": "".join(component_content)})
        return content

    def generate(self):
        content = []
        content = content + self._get_component_content(self._peripherals)
        content = content + self._get_component_content([self._model])
        return content

