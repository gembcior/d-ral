from pathlib import Path
from typing import Dict, List

from .base import BaseFormat


class MbedAutomatifyFormat(BaseFormat):
    def __init__(self, directory: Path, device: str, family: str, brand: str):
        self._directory = directory
        self._device = device
        self._brand = brand
        self._family = family
        self._device_file_content = "class dral():\n" + "    def __init__(self, proxy):\n"

    def _create_file(self, name: str, directory: Path, content: str) -> None:
        file_path = directory / name
        with open(file_path, "w", encoding="UTF-8") as new_file:
            new_file.writelines(content)

    def _create_output_directory(self, output: Path) -> Path:
        directory_path = output / f"{self._brand}" / f"{self._family}" / f"{self._device}"
        directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path

    def _create_device_file(self, name: str, directory: Path, objects: List[Dict[str, str]]) -> None:
        content = ""
        for item in objects:
            content += f"from .{item['name'].lower()} import {item['name'].capitalize()}\n"
        content += "\n" * 2
        content += self._device_file_content
        for item in objects:
            content += f"{' ' * 8}self.{item['name'].lower()} = {item['name'].capitalize()}(proxy)\n"
        self._create_file(name, directory, content)

    def _create_init_files(self, directory: Path) -> None:
        with open(directory / "__init__.py", "w", encoding="UTF-8") as init:
            init.write("from .dral import dral")
        directory = directory.parent
        while directory != self._directory:
            open(directory / "__init__.py", "w", encoding="UTF-8").close()
            directory = directory.parent

    def _make_default(self, objects: List[Dict[str, str]]) -> None:
        directory = self._create_output_directory(self._directory)
        for item in objects:
            self._create_file("%s.py" % item["name"].lower(), directory, item["content"])
        self._create_device_file("dral.py", directory, objects)
        self._create_init_files(directory)

    def _make_single(self, objects: List[Dict[str, str]]) -> None:
        pass
