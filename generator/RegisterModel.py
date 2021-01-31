from Object import Object


class RegisterModel(Object):
    def __init__(self):
        self._name = None
        self._template = "model/default.dral"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
