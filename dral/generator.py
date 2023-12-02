from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from .types import Device


@dataclass
class DralOutputFile:
    name: str
    content: str


def get_system_mapping() -> Dict[str, Any]:
    output = {
        "year": str(datetime.now().year),
    }
    return output


class DralGenerator:
    def __init__(self, template: Union[Path, List[Path]]) -> None:
        self._template = template

    def generate(self, device: Device, mapping: Optional[Dict[str, Any]] = None) -> List[DralOutputFile]:
        device_mapping = device.asdict()
        del device_mapping["device"]["peripherals"]
        variables = {
            **device_mapping,
            "system": get_system_mapping(),
            "peripheral": {},
        }
        loader = FileSystemLoader(self._template)
        env = Environment(loader=loader)
        output = []
        for peripheral in device.peripherals:
            variables["peripheral"] = peripheral.asdict()
            if mapping is not None:
                variables.update(mapping)
            template = env.get_template("peripheral.dral")
            content = template.render(**variables)
            dral_output_file = DralOutputFile(peripheral.name, content)
            output.append(dral_output_file)
        try:
            template = env.get_template("device.dral")
        except TemplateNotFound:
            return output
        content = template.render(**variables)
        dral_output_file = DralOutputFile(device.name, content)
        output.append(dral_output_file)
        return output
