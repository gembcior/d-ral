import RegisterFileParser as register_parser
import argparse
import os


class Generator:
    def __init__(self, peripherals):
        self._peripherals = peripherals

    def generate(self):
        for item in self._peripherals:
            print(item.info)


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
    reg_file = os.path.join(generator_path, "..", "regs", args.brand, args.family, "%s.yaml" % args.chip)
    peripherals = register_parser.RegisterFileParser().parse(reg_file)
    Generator(peripherals).generate()


if __name__ == "__main__":
    main()

