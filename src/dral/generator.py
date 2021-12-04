from .objects import DralDevice
from pathlib import Path
import importlib.resources as resources


class Generator:
    def __init__(self, adapter):
        self._adapter = adapter

    def _get_template(self, namespace, name):
        with resources.path("dral.templates.%s" % namespace, name) as template:
            return Path(template)

    def _create_output_directory(self, output):
        directory_path = output / "dral/inc/dral"
        Path.mkdir(directory_path, parents=True, exist_ok=True)
        return directory_path

    def _create_file(self, name, directory, content):
        file_path = directory / name
        with open(file_path, "w") as new_file:
            new_file.writelines(content)

    def _create_register_model_file(self, directory, template="default"):
        model = self._get_template(template, "model.dral")
        with open(model, "r") as f:
            self._create_file("register_model.h", directory, f.read())

    def _create_cmake_file(self, directory, template="default"):
        cmake = self._get_template(template, "cmake.dral")
        with open(cmake, "r") as f:
            self._create_file("CMakeLists.txt", directory, f.read())

    def generate(self, output, template="default", exclude=[]):
        data = self._adapter.convert()
        device = DralDevice(data["device"], template=template, exclude=exclude)
        objects = device.parse()
        directory = self._create_output_directory(output)
        for item in objects:
            self._create_file("%s.h" % item["name"].lower(), directory, item["content"])
        self._create_register_model_file(directory, template=template)
        self._create_cmake_file(output / "dral", template=template)
