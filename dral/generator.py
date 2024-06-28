from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from dral.name import lower_camel_case, upper_camel_case
from dral.objects import DralDevice


@dataclass
class DralOutputFile:
    name: str
    content: str

    def asdict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class DralGenerator:
    def __init__(self, template_dir: list[Path], forbidden_words: list[str] | None = None):
        self._template_dir = template_dir
        self._forbidden_words = forbidden_words if forbidden_words else []

    def _is_multi_instance_group(self, group: dict[str, Any]) -> bool:
        return len(group["instances"]) > 1

    def _is_dral_register(self, dral_object: dict[str, Any]) -> bool:
        return dral_object["dral_object"] == "DralRegister"

    def _is_dral_group(self, dral_object: dict[str, Any]) -> bool:
        return dral_object["dral_object"] == "DralGroup"

    def _is_top_level_group(self, group: dict[str, Any]) -> bool:
        return len(group["parent"]) == 1

    def _has_non_uniform_offset(self, group: dict[str, Any]) -> bool:
        return isinstance(group["offset"], list)

    def _get_system_mapping(self) -> dict[str, Any]:
        output = {
            "year": str(datetime.now().year),
        }
        return output

    def _get_jinja_enviroment(self) -> Environment:
        loader = FileSystemLoader(self._template_dir)
        env = Environment(loader=loader, lstrip_blocks=True, trim_blocks=True)
        env.filters["isForbidden"] = lambda x: x + "_" if x.lower() in self._forbidden_words else x
        env.filters["upperCamelCase"] = upper_camel_case
        env.filters["lowerCamelCase"] = lower_camel_case
        env.tests["multiInstance"] = self._is_multi_instance_group
        env.tests["dralRegister"] = self._is_dral_register
        env.tests["dralGroup"] = self._is_dral_group
        env.tests["topLevelGroup"] = self._is_top_level_group
        env.tests["nonUniformOffset"] = self._has_non_uniform_offset
        return env

    def generate(self, template: str, device: DralDevice) -> list[DralOutputFile]:
        env = self._get_jinja_enviroment()
        jinja_template = env.get_template(template)
        output = []
        for group in device.groups:
            variables = {"system": self._get_system_mapping(), "device": device.name, "root": group.asdict()}
            output.append(DralOutputFile(group.name, jinja_template.render(**variables)))
        return output
