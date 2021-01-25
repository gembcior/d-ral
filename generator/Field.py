from Object import Object
import os
import re


class Field(Object):
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

    def _get_pattern_substitution(self, pattern):
        substitution = "ERROR"
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

    def generate(self):
        content = []
        generator_path = os.path.dirname(os.path.realpath(__file__))
        field_template = os.path.join(generator_path, "..", "templates", "field.dral")
        dral_pattern = re.compile('\[dral\](.*?)\[#dral\]')
        with open(field_template,"r") as template:
            for line in template.readlines():
                for pattern in re.findall(dral_pattern, line):
                    substitution = self._get_pattern_substitution(pattern)
                    line = re.sub("\[dral\]%s\[#dral\]" % pattern, substitution, line)
                content.append(line)
        return content
