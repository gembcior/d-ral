from __future__ import annotations

from pathlib import Path

from dral.core.generator import DralOutputFile

from .base import DralLayout


class HtmlLayout(DralLayout):
    def __init__(self, directory: Path):
        self._directory = directory / "dralOutput" / "html"

    def _create_file(self, name: str, directory: Path, content: str) -> None:
        file_path = directory / name
        with open(file_path, "w", encoding="UTF-8") as new_file:
            new_file.writelines(content)

    def _create_output_directory(self, output: Path, device: str) -> Path:
        directory_path = output / device
        Path.mkdir(directory_path, parents=True, exist_ok=True)
        return directory_path

    def make(self, objects: list[DralOutputFile], device: str) -> None:
        directory = self._create_output_directory(self._directory, device)
        for item in objects:
            self._create_file(f"{item.name.lower()}.html", directory, item.content)
