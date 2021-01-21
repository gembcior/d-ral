import DeviceFileParser as device_file_parser
import argparse
import os


class Generator:
    def __init__(self):
        pass

    def _create_directory(self, brand, family, chip):
        generator_path = os.path.dirname(os.path.realpath(__file__))
        directory_path = os.path.join(generator_path, "..", "dral_%s_%s_%s" % (brand, family, chip), brand, family, chip)
        os.makedirs(directory_path, exist_ok=True)
        return directory_path

    def _generate_peripheral_file(self, directory, peripheral):
        peripheral_file = os.path.join(directory, "%s.h" % peripheral.name)
        content = ["Here will be generated content for this peripheral file.\n", "Stay tuned.\n"]
        with open(peripheral_file, "w") as new_file:
            new_file.writelines(content)

    def generate(self, device_data):
        directory = self._create_directory(device_data["brand"], device_data["family"], device_data["chip"])
        for peripheral in device_data["peripherals"]:
            self._generate_peripheral_file(directory, peripheral)


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

    generator_path = os.path.dirname(os.path.realpath(__file__))
    device_file = os.path.join(generator_path, "..", "devices", args.brand, args.family, "%s.yaml" % args.chip)
    device_data = device_file_parser.DeviceFileParser().parse(device_file)
    Generator().generate(device_data)


if __name__ == "__main__":
    main()

