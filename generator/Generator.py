from Constant import DEVICES_PATH
from Constant import GENERATOR_PATH
from DeviceFileParser import DeviceFileParser
import argparse
import os


class Generator:
    def __init__(self):
        self._brand = None
        self._family = None
        self._chip = None
        self._peripherals = None

    def _create_directory(self, brand, family, chip):
        directory_path = os.path.join(GENERATOR_PATH, "..", "dral_%s_%s_%s" % (brand, family, chip), brand, family, chip)
        os.makedirs(directory_path, exist_ok=True)
        return directory_path

    def _create_file(self, file, directory, content):
        file_path = os.path.join(directory, "%s.h" % file)
        with open(file_path, "w") as new_file:
            new_file.writelines(content)

    def generate(self, device):
        directory = self._create_directory(device.brand, device.family, device.chip)
        for item in device.generate():
            self._create_file(item["name"], directory, item["content"])


def main():
    parser = argparse.ArgumentParser(description='Arguments')
    parser.add_argument("-b", "--brand",
                        dest="brand", required=True,
                        help='MCU brand name.')
    parser.add_argument("-f", "--family",
                        dest="family", required=True,
                        help="MCU family name.")
    parser.add_argument("-c", "--chip",
                        dest="chip", required=True,
                        help='MCU part name.')

    args = parser.parse_args()

    device_file = os.path.join(DEVICES_PATH, args.brand, args.family, "%s.yaml" % args.chip)
    device = DeviceFileParser().parse(device_file)
    Generator().generate(device)


if __name__ == "__main__":
    main()

