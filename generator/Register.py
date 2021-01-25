from Object import Object
import os
import re


class Register(Object):
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

    def _get_pattern_substitution(self, pattern):
        substitution = "ERROR"
        pattern = pattern.split(".")
        if pattern[0] == "register":
            if pattern[1] == "name":
                substitution = self._name
            elif pattern[1] == "offset":
                substitution = "0x%04X" % self._offset
            elif pattern[1] == "policy":
                substitution = self._get_policy(self._policy)
            elif pattern[1] == "fields":
                content = []
                for field in self._fields:
                    content.append("".join(field.generate()))
                substitution = "".join(content)
                substitution = ("  ".join(("\n" + substitution).splitlines(True))).lstrip("\n")
        if len(pattern) > 2:
            substitution = self._apply_modifier(substitution, pattern[2])
        return substitution

    def generate(self):
        content = []
        generator_path = os.path.dirname(os.path.realpath(__file__))
        register_template = os.path.join(generator_path, "..", "templates", "register.dral")
        dral_pattern = re.compile('\[dral\](.*?)\[#dral\]')
        with open(register_template,"r") as template:
            for line in template.readlines():
                for pattern in re.findall(dral_pattern, line):
                    substitution = self._get_pattern_substitution(pattern)
                    line = re.sub("\[dral\]%s\[#dral\]" % pattern, substitution, line)
                content.append(line)
        return content
