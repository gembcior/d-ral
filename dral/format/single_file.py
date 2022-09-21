from pathlib import Path
from typing import Dict, List


class SingleFileFormat:
    def __init__(self, directory: Path, name: str, includeRegModel: bool = False):
        self._directory = directory
        self._name = name
        self._includeRegModel = includeRegModel

    def _create_file(self, name: str, directory: Path, content: str) -> None:
        file_path = directory / name
        with open(file_path, "w", encoding="UTF-8") as new_file:
            new_file.writelines(content)

    def _create_output_directory(self, output: Path) -> Path:
        output.mkdir(parents=True, exist_ok=True)
        return self._directory

    def make(self, objects: List[Dict[str, str]]) -> None:
        directory = self._create_output_directory(self._directory)
        file_path = self._directory / f"{self._name}"
        self._create_file(file_path.name, directory, "")

        for i, item in enumerate(objects):
            if item["name"] == "register_model" and not self._includeRegModel:
                self._create_file(f"{item['name'].lower()}.h", directory, item["content"])
            else:
                with open(file_path, "a", encoding="UTF-8") as new_file:
                    if i > 0:
                        new_file.write("\n\n")
                    new_file.writelines(item["content"])
