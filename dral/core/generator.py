from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader
from natsort import natsorted

from dral.core.objects import DralDevice, DralSuffix
from dral.utils.name import decapitalize, lower_camel_case, upper_camel_case


@dataclass
class DralOutputFile:
    name: str
    content: str

    def asdict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class DralGenerator(ABC):
    def __init__(self, template_dir: list[Path], suffix: type[DralSuffix] = DralSuffix, forbidden_words: list[str] | None = None):
        self._template_dir = template_dir
        self._suffix = suffix()
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
        return any(len(parent["instances"]) > 1 for parent in group["parent"])

    def _get_hierarchy(self, dral_object: dict[str, Any]) -> str:
        if len(dral_object["parent"]) <= 1:
            return str(dral_object["name"])
        hierarchy = ""
        for parent in dral_object["parent"][1:]:
            hierarchy += f"{parent['name']}::"
        hierarchy += dral_object["name"]
        return str(hierarchy)

    def _get_instances_info(self, dral_object: dict[str, Any]) -> list[tuple[str, str]]:
        if dral_object["dral_object"] == "DralGroup":
            output = [(instance["name"], instance["address"]) for instance in dral_object["instances"]]
        else:
            output = [(dral_object["name"], dral_object["address"])]
        for parent in reversed(dral_object["parent"][1:]):
            partial = []
            for item in output:
                for i, instance in enumerate(parent["instances"]):
                    if isinstance(parent["offset"], list):
                        partial.append((f"{instance['name']}::{item[0]}", item[1] + parent["address"] + parent["offset"][i]))
                    else:
                        partial.append((f"{instance['name']}::{item[0]}", item[1] + parent["address"] + i * parent["offset"]))
            output = partial
        return natsorted(output, key=lambda x: x[1])

    def _get_absolute_address(self, dral_object: dict[str, Any]) -> int:
        address = int(dral_object["address"])
        if len(dral_object["parent"]) <= 1:
            return address
        for parent in dral_object["parent"][1:]:
            address += int(parent["address"])
        return address

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
        env.filters["decapitalize"] = decapitalize
        env.tests["multiInstance"] = self._is_multi_instance_group
        env.tests["dralRegister"] = self._is_dral_register
        env.tests["dralGroup"] = self._is_dral_group
        env.tests["topLevelGroup"] = self._is_top_level_group
        env.tests["nonUniformOffset"] = self._has_non_uniform_offset
        env.tests["inMultiInstanceScope"] = self._in_multi_instance_scope
        env.filters["hierarchy"] = self._get_hierarchy
        env.filters["instancesInfo"] = self._get_instances_info
        env.filters["absoluteAddress"] = self._get_absolute_address
        return env

    @abstractmethod
    def generate(self, template: str, device: DralDevice) -> list[DralOutputFile] | DralOutputFile:
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
