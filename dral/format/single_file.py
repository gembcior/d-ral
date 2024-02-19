from __future__ import annotations

from pathlib import Path
from typing import List

from dral.format.base import BaseFormat

from ..generator import DralOutputFile


class SingleFileFormat(BaseFormat):
    def __init__(self, directory: Path, device: str, name: str):
        self._directory = directory
        self._device = device
        self._name = name

    def _create_file(self, name: str, directory: Path, content: str) -> None:
        file_path = directory / name
        with open(file_path, "w", encoding="UTF-8") as new_file:
            new_file.writelines(content)

    def _create_output_directory(self, output: Path) -> Path:
        directory_path = output / f"{self._device}"
        directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path

    def _merge_content(self, objects: List[DralOutputFile]) -> DralOutputFile:
        output = DralOutputFile(name=self._name, content="")
        for item in objects:
            output.content += item.content
        return output

    def _make_default(self, objects: List[DralOutputFile], _=None) -> None:
        directory = self._create_output_directory(self._directory)
        item = self._merge_content(objects)
        self._create_file(f"{item.name.lower()}", directory, item.content)
