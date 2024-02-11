from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from .types import Device, MultiPeripheralDevice, Peripheral, SinglePeripheralDevice


@dataclass
class DralOutputFile:
    name: str
    content: str


class DralGenerator:
    def __init__(self, forbidden_words: Optional[Path], mapping: Optional[Path]) -> None:
        self._mapping = None
        if mapping is not None:
            with open(mapping, "r", encoding="utf-8") as mapping_file:
                self._mapping = yaml.load(mapping_file, Loader=yaml.FullLoader)
        self._forbidden_words = []
        if forbidden_words is not None:
            with open(forbidden_words, "r", encoding="UTF-8") as forbidden_words_file:
                self._forbidden_words = yaml.load(forbidden_words_file, Loader=yaml.FullLoader)

    def _get_system_mapping(self) -> Dict[str, Any]:
        output = {
            "year": str(datetime.now().year),
        }
        return output

    def _generate(self, template_name: str, template_dir: Union[Path, List[Path]], variables: Dict[str, Any]) -> str:
        loader = FileSystemLoader(template_dir)
        env = Environment(loader=loader)
        env.filters["isforbidden"] = lambda x: x + "_" if x.lower() in self._forbidden_words else x
        template = env.get_template(template_name)
        return template.render(**variables)

    def _get_peripherals(self, peripherals: List[Peripheral], template_dir: Union[Path, List[Path]], variables: Dict[str, Any]) -> List[DralOutputFile]:
        output = []
        for peripheral in peripherals:
            variables["peripheral"] = peripheral.asdict()
            if self._mapping is not None:
                variables.update(self._mapping)
            content = self._generate("peripheral.dral", template_dir, variables)
            del variables["peripheral"]
            output.append(DralOutputFile(peripheral.name, content))
        return output

    def _get_device(self, device: Device, template_dir: Union[Path, List[Path]], variables: Dict[str, Any]) -> DralOutputFile:
        content = self._generate("device.dral", template_dir, variables)
        return DralOutputFile(device.name, content)

    def _get_multi_peripheral_output(self, device: MultiPeripheralDevice, template_dir: Union[Path, List[Path]]) -> List[DralOutputFile]:
        variables = {
            **device.asdict(),
            "system": self._get_system_mapping(),
        }
        output = self._get_peripherals(device.peripherals, template_dir, variables)
        try:
            output.append(self._get_device(device, template_dir, variables))
        except TemplateNotFound:
            pass
        return output

    def _get_single_peripheral_output(self, device: SinglePeripheralDevice, template_dir: Union[Path, List[Path]]) -> list[DralOutputFile]:
        raise NotImplementedError

    def get_model(self, template_dir: Union[Path, List[Path]]) -> DralOutputFile:
        variables = {
            "system": self._get_system_mapping(),
        }
        if self._mapping is not None:
            variables.update(self._mapping)
        model_content = self._generate(
            "model.dral",
            template_dir,
            variables,
        )
        return DralOutputFile("register_model", model_content)

    def get_output(self, device: Union[MultiPeripheralDevice, SinglePeripheralDevice], template_dir: Union[Path, List[Path]]) -> List[DralOutputFile]:
        if isinstance(device, MultiPeripheralDevice):
            return self._get_multi_peripheral_output(device, template_dir)
        elif isinstance(device, SinglePeripheralDevice):
            return self._get_single_peripheral_output(device, template_dir)
        else:
            raise TypeError("Invalid device type")
