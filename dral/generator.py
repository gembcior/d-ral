from __future__ import annotations

from typing import Dict, List, Optional, Union

from .mapping import DralMapping
from .template import DralTemplate
from .types import Device


class DralGenerator:
    def __init__(self, template: DralTemplate) -> None:
        self._template = template

    def generate(self, device: Device, exclude: Union[None, List[str]] = None, mapping: Optional[DralMapping] = None) -> List[Dict[str, str]]:
        device_mapping = device.asdict()
        del device_mapping["device"]["peripherals"]
        peripheral_file_content = []
        for peripheral in device.peripherals:
            peripheral_mapping = peripheral.asdict()
            peripheral_mapping.update(device_mapping)
            content = self._template.parse_from_template("peripheral.dral", peripheral_mapping)
            peripheral_file_content.append({"name": peripheral.name, "content": "".join(content)})
        if self._template.exists("model.dral"):
            peripheral_file_content.append({"name": "register_model", "content": self._template.read("model.dral")})
        return peripheral_file_content
