from DralObject import DralObject


class RegisterModel(DralObject):
    def __init__(self):
        super().__init__()
        self._name = None
        self._template = "model/default.dral"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
