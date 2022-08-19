from typing import Dict, List, Union, overload

from .objects import DralDevice
from .types import Device, Peripheral
from .utils import Utils


class Generator:
    @overload
    def __init__(self) -> None:
        ...
    @overload
    def __init__(self, template: str) -> None:
        ...
    def __init__(self, template = "default"):
        self._template = template

    def _get_register_model_content(self):
        model = Utils.get_template(self._template, "model.dral")
        with open(model, "r") as f:
            return f.read()

    def generate(self, device: Device, exclude: List[str] = []) -> List[Dict]:
        dral_device = DralDevice(device, self._template, exclude=exclude)
        objects = dral_device.parse()
        if Utils.get_template(self._template, "model.dral").exists():
            objects.append({"name": "register_model", "content": self._get_register_model_content()})
        return objects
