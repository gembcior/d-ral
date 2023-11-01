from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from ..generator import DralOutputFile
from .base import BaseFormat


class PythonFormat(BaseFormat):
    def __init__(self, directory: Path, device: str):
        self._directory = directory / "python"
        self._device = device

    def _create_file(self, name: str, directory: Path, content: str) -> None:
        file_path = directory / name
        with open(file_path, "w", encoding="UTF-8") as new_file:
            new_file.writelines(content)

    def _create_output_directory(self, output: Path) -> Path:
        directory_path = output / f"{self._device}"
        directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path

    def _make_default(self, objects: List[DralOutputFile], model: Optional[DralOutputFile] = None) -> None:
        directory = self._create_output_directory(self._directory)
        for item in objects:
            self._create_file(f"{item.name.lower()}.py", directory, item.content)
        if model is not None:
            self._create_file(f"{model.name.lower()}.py", self._directory, model.content)
