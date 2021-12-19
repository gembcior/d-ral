from pathlib import Path
from typing import List


class SingleFileFormat:
    def __init__(self, directory: Path, name: str):
        self._directory = directory
        self._name = name

    def make(self, objects: List):
        content = objects[0]["content"]
        if len(objects) > 1:
            for item in objects[1:]:
                content += f"\n\n{item['content']}"
        Path.mkdir(self._directory, parents=True, exist_ok=True)
        file_path = self._directory / self._name
        with open(file_path, "w") as new_file:
            new_file.writelines(content)


class CMakeLibFormat:
    def __init__(self, directory: Path, name: str):
        self._directory = directory
        self._name = name
        self._cmake_content = (f"add_library({self._name} INTERFACE)\n"
                               f"\n"
                               f"target_include_directories({self._name}\n"
                               f"  INTERFACE\n"
                               f"    ${{CMAKE_CURRENT_SOURCE_DIR}}/inc\n"
                               f")")

    def _create_file(self, name, directory, content):
        file_path = directory / name
        with open(file_path, "w") as new_file:
            new_file.writelines(content)

    def _create_output_directory(self, output):
        directory_path = output / f"{self._name}/inc/{self._name}"
        Path.mkdir(directory_path, parents=True, exist_ok=True)
        return directory_path

    def make(self, objects: List):
        directory = self._create_output_directory(self._directory)
        for item in objects:
            self._create_file("%s.h" % item["name"].lower(), directory, item["content"])
        self._create_file("CMakeLists.txt", self._directory / self._name, self._cmake_content)
