from typing import Dict, List, Union

from .objects import DralDevice
from .types import Device
from .utils import Utils


class Generator:
    def __init__(self, template: str = "default") -> None:
        self._template = template

    def _get_register_model_content(self) -> str:
        model = Utils.get_template(self._template, "model.dral")
        with open(model, "r", encoding="UTF-8") as file:
            return file.read()

    def generate(self, device: Device, exclude: Union[None, List[str]] = None) -> List[Dict[str, str]]:
        dral_device = DralDevice(device, self._template, exclude=exclude)
        objects = dral_device.parse()
        if Utils.get_template(self._template, "model.dral").exists():
            objects.append(
                {
                    "name": "register_model",
                    "content": self._get_register_model_content(),
                }
            )
        return objects
