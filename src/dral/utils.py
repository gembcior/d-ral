import importlib.resources as resources
from pathlib import Path


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
