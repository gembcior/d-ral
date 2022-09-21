from pathlib import Path
from typing import Dict, List

from .base import BaseFormat


class CMakeLibFormat(BaseFormat):
    def __init__(self, directory: Path, name: str):
        self._directory = directory
        self._name = name
        self._cmake_content = (
            f"add_library({self._name} INTERFACE)\n"
            f"\n"
            f"target_include_directories({self._name}\n"
            f"  INTERFACE\n"
            f"    ${{CMAKE_CURRENT_SOURCE_DIR}}/inc\n"
            f")"
        )

    def _create_file(self, name: str, directory: Path, content: str) -> None:
        file_path = directory / name
        with open(file_path, "w", encoding="UTF-8") as new_file:
            new_file.writelines(content)

    def _create_output_directory(self, output: Path) -> Path:
        directory_path = output / f"{self._name}/inc/{self._name}"
        Path.mkdir(directory_path, parents=True, exist_ok=True)
        return directory_path

    def _make_default(self, objects: List[Dict[str, str]]) -> None:
        directory = self._create_output_directory(self._directory)
        for item in objects:
            self._create_file("%s.h" % item["name"].lower(), directory, item["content"])
        self._create_file("CMakeLists.txt", self._directory / self._name, self._cmake_content)

    def _make_single(self, objects: List[Dict[str, str]]) -> None:
        # TODO refactor
        from .single_file import SingleFileFormat

        single = SingleFileFormat(self._directory, "dral.h")
        single.make(objects)
