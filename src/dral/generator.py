from .objects import DralDevice
from pathlib import Path
import importlib.resources as resources


class Utils:
    def __init__(self, template, template_path=None):
        self._template = template
        self._template_path = template_path

    def get_template(self, name):
        if self._template_path is not None:
            return Path(self._template_path) / name
        else:
            with resources.path("dral.templates.%s" % self._template, name) as template:
                return Path(template)


class Generator:
    def __init__(self, adapter, template="default", template_path=None):
        self._adapter = adapter
        self._utils = Utils(template, template_path)

    def _get_register_model_content(self):
        model = self._utils.get_template("model.dral")
        with open(model, "r") as f:
            return f.read()

    def generate(self, exclude=[]):
        data = self._adapter.convert()
        device = DralDevice(data["device"], utils=self._utils, exclude=exclude)
        objects = device.parse()
        if self._utils.get_template("model.dral").exists():
            objects.append({"name": "register_model", "content": self._get_register_model_content()})
        return objects
