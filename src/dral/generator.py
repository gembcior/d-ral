from .objects import DralDevice
import svd2py
import os

# TODO to be removed remove
from rich import print

class Generator:
    def __init__(self, svd_file):
        self._svd_file = svd_file

    def _create_directory(self, output):
        directory_path = os.path.join(output, "dral")
        os.makedirs(directory_path, exist_ok=True)
        return directory_path

    def _create_file(self, name, directory, content):
        file_path = os.path.join(directory, "%s.h" % name)
        with open(file_path, "w") as new_file:
            new_file.writelines(content)

    def generate(self, output):
        svd = svd2py.SvdParser(self._svd_file)
        svd = svd.convert()
        device = DralDevice(svd["device"])
        objects = device.parse()
        directory = self._create_directory(output)
        for item in objects:
            self._create_file(item["name"].lower(), directory, item["content"])

