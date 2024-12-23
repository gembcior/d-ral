from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from dral.core.objects import DralDevice, DralSuffix
from dral.utils.name import lower_camel_case, upper_camel_case


@dataclass
class DralOutputFile:
    name: str
    content: str

    def asdict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class DralGenerator(ABC):
    def __init__(self, template_dir: list[Path], suffix: DralSuffix = DralSuffix(), forbidden_words: list[str] | None = None):
        self._template_dir = template_dir
        self._suffix = suffix
        self._forbidden_words = forbidden_words if forbidden_words else []

    def _is_multi_instance_group(self, group: dict[str, Any]) -> bool:
        if "instances" not in group:
            return False
        return len(group["instances"]) > 1

    def _is_dral_register(self, dral_object: dict[str, Any]) -> bool:
        return bool(dral_object["dral_object"] == "DralRegister")

    def _is_dral_group(self, dral_object: dict[str, Any]) -> bool:
        return bool(dral_object["dral_object"] == "DralGroup")

    def _is_top_level_group(self, group: dict[str, Any]) -> bool:
        return len(group["parent"]) == 1

    def _has_non_uniform_offset(self, group: dict[str, Any]) -> bool:
        return isinstance(group["offset"], list)

    def _in_multi_instance_scope(self, group: dict[str, Any]) -> bool:
        for parent in group["parent"]:
            if len(parent["instances"]) > 1:
                return True
        return False

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
        env.tests["inMultiInstanceScope"] = self._in_multi_instance_scope
        return env

    @abstractmethod
    def generate(self, template: str, device: DralDevice) -> Any:
        pass


class SingleOutputGenerator(DralGenerator):
    def generate(self, template: str, device: DralDevice) -> DralOutputFile:
        env = self._get_jinja_enviroment()
        jinja_template = env.get_template(template)
        variables = {
            "system": self._get_system_mapping(),
            "device": device.name,
            "root": device.asdict(),
            "suffix": self._suffix.asdict(),
        }
        return DralOutputFile(device.name, jinja_template.render(**variables))


class MultiOutputGenerator(DralGenerator):
    def generate(self, template: str, device: DralDevice) -> list[DralOutputFile]:
        env = self._get_jinja_enviroment()
        jinja_template = env.get_template(template)
        output = []
        for group in device.groups:
            variables = {
                "system": self._get_system_mapping(),
                "device": device.name,
                "root": group.asdict(),
                "suffix": self._suffix.asdict(),
            }
            output.append(DralOutputFile(group.name, jinja_template.render(**variables)))
        return output
