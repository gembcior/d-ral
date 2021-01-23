import DeviceFileParser as device_file_parser
import argparse
import os
import re


class Generator:
    def __init__(self):
        self._brand = None
        self._family = None
        self._chip = None
        self._peripherals = None

    def _create_directory(self, brand, family, chip):
        generator_path = os.path.dirname(os.path.realpath(__file__))
        directory_path = os.path.join(generator_path, "..", "dral_%s_%s_%s" % (brand, family, chip), brand, family, chip)
        os.makedirs(directory_path, exist_ok=True)
        return directory_path

    def _get_register_policy(self, pattern):
        policy = "ERROR"
        if pattern.lower() == "r":
            policy = "ReadOnly"
        elif pattern.lower() == "w":
            policy = "WriteOnly"
        elif pattern.lower() == "rw":
            policy = "ReadWrite"
        elif pattern.lower() == "rc_w1":
            policy = "ReadWrite"
        elif pattern.lower() == "rc_w0":
            policy = "ReadWrite"
        elif pattern.lower() == "rs":
            policy = "ReadWrite"
        elif pattern.lower() == "rt_w":
            policy = "ReadWrite"
        elif pattern.lower() == "t":
            policy = "WriteOnly"
        return policy

    def _get_pattern_substitution(self, pattern, data=None):
        substitution = "ERROR"
        pattern = pattern.split(".")
        if pattern[0] == "brand":
            substitution = self._brand
        elif pattern[0] == "family":
            substitution = self._family
        elif pattern[0] == "chip":
            substitution = self._chip
        elif pattern[0] == "peripheral":
            if pattern[1] == "name":
                substitution = data.name
            elif pattern[1] == "address":
                substitution = "0x%08X" % data.address
            elif pattern[1] == "include_guard":
                substitution = "DRAL_%s_%s_%s_%s_H" % (self._brand.upper(), self._family.upper(), self._chip.upper(), data.name.upper())
            elif pattern[1] == "registers":
                substitution = "".join(self._get_registers_content(data.registers))
        elif pattern[0] == "register":
            if pattern[1] == "name":
                substitution = data.name
            elif pattern[1] == "offset":
                substitution = "0x%04X" % data.offset
            elif pattern[1] == "policy":
                substitution = self._get_register_policy(data.policy)
            elif pattern[1] == "fields":
                substitution = "".join(self._get_fields_content(data.fields))
                substitution = ("  ".join(("\n" + substitution).splitlines(True))).lstrip("\n")
        elif pattern[0] == "field":
            if pattern[1] == "name":
                substitution = "%-12s" % data.name
            elif pattern[1] == "position":
                substitution = "%2d" % data.position
            elif pattern[1] == "policy":
                substitution = self._get_register_policy(data.policy)
            elif pattern[1] == "mask":
                substitution = "0x%08X" % data.mask
        return substitution

    def _get_fields_content(self, fields):
        content = []
        generator_path = os.path.dirname(os.path.realpath(__file__))
        field_template = os.path.join(generator_path, "..", "templates", "field.dral")
        dral_pattern = re.compile('\[dral\](.*?)\[#dral\]')
        for field in fields:
            with open(field_template,"r") as template:
                for line in template.readlines():
                    for pattern in re.findall(dral_pattern, line):
                        substitution = self._get_pattern_substitution(pattern, field)
                        line = re.sub("\[dral\]%s\[#dral\]" % pattern, substitution, line)
                    content.append(line)
        return content

    def _get_registers_content(self, registers):
        content = []
        generator_path = os.path.dirname(os.path.realpath(__file__))
        register_template = os.path.join(generator_path, "..", "templates", "register.dral")
        dral_pattern = re.compile('\[dral\](.*?)\[#dral\]')
        for reg in registers:
            with open(register_template,"r") as template:
                for line in template.readlines():
                    for pattern in re.findall(dral_pattern, line):
                        substitution = self._get_pattern_substitution(pattern, reg)
                        line = re.sub("\[dral\]%s\[#dral\]" % pattern, substitution, line)
                    content.append(line)
            content.append("\n")
        return content

    def _get_peripheral_file_content(self, peripheral):
        content = []
        generator_path = os.path.dirname(os.path.realpath(__file__))
        peripheral_file_template = os.path.join(generator_path, "..", "templates", "peripheral_file.dral")
        dral_pattern = re.compile('\[dral\](.*?)\[#dral\]')
        with open(peripheral_file_template,"r") as template:
            for line in template.readlines():
                for pattern in re.findall(dral_pattern, line):
                    substitution = self._get_pattern_substitution(pattern, peripheral)
                    line = re.sub("\[dral\]%s\[#dral\]" % pattern, substitution, line)
                content.append(line)
        return content

    def _get_reg_model_file_content(self):
        content = []
        generator_path = os.path.dirname(os.path.realpath(__file__))
        reg_model_file_template = os.path.join(generator_path, "..", "templates", "register_model.dral")
        dral_pattern = re.compile('\[dral\](.*?)\[#dral\]')
        with open(reg_model_file_template,"r") as template:
            for line in template.readlines():
                for pattern in re.findall(dral_pattern, line):
                    substitution = self._get_pattern_substitution(pattern)
                    line = re.sub("\[dral\]%s\[#dral\]" % pattern, substitution, line)
                content.append(line)
        return content

    def _generate_peripheral_file(self, directory, peripheral):
        peripheral_file = os.path.join(directory, "%s.h" % peripheral.name)
        content = self._get_peripheral_file_content(peripheral)
        with open(peripheral_file, "w") as new_file:
            new_file.writelines(content)

    def _generate_reg_model_file(self, directory):
        reg_model_file = os.path.join(directory, "register_model.h")
        content = self._get_reg_model_file_content()
        with open(reg_model_file, "w") as new_file:
            new_file.writelines(content)

    def generate(self, device_data):
        self._brand = device_data["brand"]
        self._family = device_data["family"]
        self._chip = device_data["chip"]
        self._peripherals = device_data["peripherals"]
        directory = self._create_directory(self._brand, self._family, self._chip)
        for peripheral in self._peripherals:
            self._generate_peripheral_file(directory, peripheral)
        self._generate_reg_model_file(directory)


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

