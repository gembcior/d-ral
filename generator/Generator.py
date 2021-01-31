from Constant import DEVICES_PATH
from Constant import GENERATOR_PATH
from DeviceFileParser import DeviceFileParser
from Device import Device
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

    def generate(self, device):
        directory = self._create_directory(device.brand, device.family, device.chip)
        files_to_create = device.generate()
        for item in files_to_create:
            file_path = os.path.join(directory, "%s.h" % item["name"])
            with open(file_path, "w") as new_file:
                new_file.writelines(item["content"])



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

