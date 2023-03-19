from pathlib import Path
from typing import Dict, List, Union

from .objects import DralDevice
from .types import Device
from .mapping import DralMapping
from .template import DralTemplate


class DralGenerator:
    def __init__(self, mapping: DralMapping, template: DralTemplate) -> None:
        self._mapping = mapping
        self._template = template

    def generate(self, device: Device, exclude: Union[None, List[str]] = None) -> List[Dict[str, str]]:
        dral_device = DralDevice(device, self._mapping, self._template, exclude=exclude)
        objects = dral_device.parse()
        if self._template.exists("model.dral"):
            objects.append(
                {
                    "name": "register_model",
                    "content": self._template.read("model.dral")
                }
            )
        return objects
