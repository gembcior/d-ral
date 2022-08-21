from pathlib import Path
from typing import List


class MbedAutomatifyFormat:
    def __init__(self, directory: Path, device: str):
        self._directory = directory
        self._device = device
        self._device_file_content = (
                f"class {self._device.upper()}():\n"
                f"    def __init__(self, proxy):\n")

    def _create_file(self, name: str, directory: Path, content: str) -> None:
        file_path = directory / name
        with open(file_path, "w") as new_file:
            new_file.writelines(content)

    def _create_output_directory(self, output: Path) -> Path:
        directory_path = output / f"{self._device}"
        directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path

    def _create_device_file(self, name: str, directory: Path, objects: List) -> None:
        content = ""
        for item in objects:
            content += f"from .{item['name'].lower()} import {item['name']}\n"
        content += "\n" * 2
        content += self._device_file_content
        for item in objects:
            content += f"{' ' * 8}self.{item['name'].lower()} = {item['name']}(proxy)\n"
        self._create_file(name, directory, content)

    def make(self, objects: List):
        directory = self._create_output_directory(self._directory)
        for item in objects:
            self._create_file("%s.py" % item["name"].lower(), directory, item["content"])
        self._create_device_file(f"{self._device}.py", directory, objects)
