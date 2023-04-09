from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .template import DralTemplate
from .types import Device


@dataclass
class DralOutputFile:
    name: str
    content: str


class DralGenerator:
    def __init__(self, template: DralTemplate) -> None:
        self._template = template

    def generate(self, device: Device, mapping: Optional[Dict[str, Any]] = None) -> List[DralOutputFile]:
        device_mapping = device.asdict()
        del device_mapping["device"]["peripherals"]
        peripheral_file_content = []
        for peripheral in device.peripherals:
            peripheral_mapping = peripheral.asdict()
            peripheral_mapping.update(device_mapping)
            if mapping is not None:
                peripheral_mapping.update(mapping)
            content = self._template.parse_from_template("peripheral.dral", peripheral_mapping)
            dral_output_file = DralOutputFile(peripheral.name, "".join(content))
            peripheral_file_content.append(dral_output_file)
        if self._template.exists("model.dral"):
            model_content = self._template.parse_from_template("model.dral", mapping={})
            dral_output_file = DralOutputFile("register_model", "".join(model_content))
            peripheral_file_content.append(dral_output_file)
        return peripheral_file_content
