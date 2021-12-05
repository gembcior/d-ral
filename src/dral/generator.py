from .objects import DralDevice
from pathlib import Path
import importlib.resources as resources


class Utils:
    def __init__(self, template, template_path=None):
        self._template = template
        self._template_path = template_path

    def get_template(self, name):
        if self._template_path is not None:
            return Path(self._template_path) / name
        else:
            with resources.path("dral.templates.%s" % self._template, name) as template:
                return Path(template)



class Generator:
    def __init__(self, adapter, template="default", template_path=None):
        self._adapter = adapter
        self._template = template
        self._template_path = template_path
        self._utils = Utils(template, template_path)

    def _create_output_directory(self, output):
        directory_path = output / "dral/inc/dral"
        Path.mkdir(directory_path, parents=True, exist_ok=True)
        return directory_path

    def _create_file(self, name, directory, content):
        file_path = directory / name
        with open(file_path, "w") as new_file:
            new_file.writelines(content)

    def _create_register_model_file(self, directory):
        model = self._utils.get_template("model.dral")
        with open(model, "r") as f:
            self._create_file("register_model.h", directory, f.read())

    def _create_cmake_file(self, directory):
        cmake = self._utils.get_template("cmake.dral")
        with open(cmake, "r") as f:
            self._create_file("CMakeLists.txt", directory, f.read())

    def generate(self, output, exclude=[]):
        data = self._adapter.convert()
        device = DralDevice(data["device"], utils=self._utils, exclude=exclude)
        objects = device.parse()
        directory = self._create_output_directory(output)
        for item in objects:
            self._create_file("%s.h" % item["name"].lower(), directory, item["content"])
        self._create_register_model_file(directory)
        self._create_cmake_file(output / "dral")
