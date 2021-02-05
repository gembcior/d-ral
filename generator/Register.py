from DralObject import DralObject


class Register(DralObject):
    def __init__(self):
        super().__init__()
        self._name = None
        self._offset = None
        self._policy = None
        self._fields = None
        self._declaration_template = "register/normal/declaration.dral"
        self._instance_template = "register/normal/instance.dral"

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

    def _get_fields_content(self):
        content = []
        for field in self._fields:
            content.append(field.get_string())
        return "".join(content)

    def _get_substitution(self, pattern):
        substitution = None
        if pattern[0] == "register":
            if pattern[1] == "name":
                substitution = self._name
            elif pattern[1] == "offset":
                substitution = "0x%04X" % self._offset
            elif pattern[1] == "policy":
                substitution = self._get_policy(self._policy)
            elif pattern[1] == "fields":
                substitution = self._get_fields_content()
                substitution = ("  ".join(("\n" + substitution).splitlines(True))).lstrip("\n")
        return substitution

    def get_declaration_string(self):
        content = self._generate_from_template(self._declaration_template)
        content = self._generate_from_string(content)
        return content

    def get_instance_string(self):
        content = self._generate_from_template(self._instance_template)
        content = self._generate_from_string(content)
        return content

    def get_string(self):
        content = self.get_declaration_string()
        content += self.get_instance_string()
        return content


class CollectionRegister(Register):
    def __init__(self):
        super().__init__()
        self._declaration_template = "register/collection/declaration.dral"
        self._instance_template = "register/collection/instance.dral"
