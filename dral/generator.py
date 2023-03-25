from pathlib import Path
from typing import Dict, List, Union, Optional

from .mapping import DralMapping
from .objects import DralDevice
from .template import DralTemplate
from .types import Device


class DralGenerator:
    def __init__(self, template: DralTemplate) -> None:
        self._template = template

    def generate(self, device: Device, exclude: Union[None, List[str]] = None, mapping: Optional[DralMapping] = None) -> List[Dict[str, str]]:
        dral_device = DralDevice(device, self._template, exclude=exclude, mapping=mapping)
        objects = dral_device.parse()
        if self._template.exists("model.dral"):
            objects.append({"name": "register_model", "content": self._template.read("model.dral")})
        return objects
