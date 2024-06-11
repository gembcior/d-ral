from __future__ import annotations

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


class DralGenerator:
    def __init__(self, template_dir: list[Path], forbidden_words: list[str] | None = None):
        self._template_dir = template_dir
        self._forbidden_words = forbidden_words if forbidden_words else []

    def _get_system_mapping(self) -> dict[str, Any]:
        output = {
            "year": str(datetime.now().year),
        }
        return output

    def generate(self, template: str, device: DralDevice) -> list[DralOutputFile]:
        loader = FileSystemLoader(self._template_dir)
        env = Environment(loader=loader, lstrip_blocks=True, trim_blocks=True)
        env.filters["isforbidden"] = lambda x: x + "_" if x.lower() in self._forbidden_words else x
        env.filters["uppercamelcase"] = upper_camel_case
        env.filters["lowercamelcase"] = lower_camel_case
        jinja_template = env.get_template(template)
        output = []
        for group in device.groups:
            variables = {"system": self._get_system_mapping(), "device": device.name, "root": group.asdict()}
            output.append(DralOutputFile(group.name, jinja_template.render(**variables)))
        return output
