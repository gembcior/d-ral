import importlib.resources as resources
from pathlib import Path


class Utils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_template(template: str, name: str) -> Path:
        with resources.path("dral.templates.%s" % template, name) as item:
            return Path(item)

    @staticmethod
    def get_svd_file(brand: str, chip: str) -> Path:
        with resources.path("dral.devices.%s" % brand, "%s.svd" % chip) as svd:
            return Path(svd)
