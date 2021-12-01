from .objects import DralDevice
import importlib.resources as resources
import svd2py
import os


class Generator:
    def __init__(self, svd_file):
        self._svd_file = svd_file

    def _get_template(self, namespace, name):
        with resources.path("dral.templates.%s" % namespace, name) as template:
            return template

    def _create_output_directory(self, output):
        directory_path = os.path.join(output, "dral", "inc", "dral")
        os.makedirs(directory_path, exist_ok=True)
        return directory_path

    def _create_file(self, name, directory, content):
        file_path = os.path.join(directory, name)
        with open(file_path, "w") as new_file:
            new_file.writelines(content)

    def _create_register_model_file(self, directory):
        model = self._get_template("model", "default.dral")
        with open(model, "r") as f:
            self._create_file("register_model.h", directory, f.read())

    def _create_cmake_file(self, directory):
        cmake = self._get_template("cmake", "default.dral")
        with open(cmake, "r") as f:
            self._create_file("CMakeLists.txt", directory, f.read())

    def generate(self, output):
        svd = svd2py.SvdParser(self._svd_file)
        svd = svd.convert()
        device = DralDevice(svd["device"])
        objects = device.parse()
        directory = self._create_output_directory(output)
        for item in objects:
            self._create_file("%s.h" % item["name"].lower(), directory, item["content"])
        self._create_register_model_file(directory)
        self._create_cmake_file(os.path.join(output, "dral"))
