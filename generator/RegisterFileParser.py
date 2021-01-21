import Peripheral as peripheral
import Register as register
import Field as field
import yaml
import os
import re


class RegisterFileParser:
    def __init__(self):
        pass

    def _get_peripherals(self, reg_file, peripherals):
        with open(reg_file, "r") as yaml_file:
            peripherals.update(yaml.load(yaml_file, Loader=yaml.FullLoader)["peripherals"])

        include_file_list = []
        with open(reg_file, "r") as yaml_file:
            include_file_pattern = re.compile('"(.*?)"')
            for line in yaml_file.readlines():
                if line.startswith("#include"):
                    include_file_list.append(os.path.join(os.path.dirname(reg_file), re.findall(include_file_pattern, line)[0]))

        for include_file in include_file_list:
            self._get_peripherals(include_file, peripherals)

    def _parse_peripherals(self, peripherals):
        peripherals_list = []
        for item in peripherals:
            new_peripheral = peripheral.Peripheral()
            new_peripheral.name = item
            new_peripheral.address = int(peripherals[item]["address"])
            new_peripheral.registers = self._parse_registers(peripherals[item]["registers"])
            peripherals_list.append(new_peripheral)
        return peripherals_list

    def _parse_registers(self, registers):
        registers_list = []
        for item in registers:
            if "range" in registers[item]:
                start = int(registers[item]["range"]["start"])
                end = int(registers[item]["range"]["end"])
                for num in range(start, end + 1):
                    new_register = register.Register()
                    new_register.name = "%s%d" % (item, num)
                    new_register.offset = int(registers[item]["offset"] + (0x04 * num))
                    new_register.policy = registers[item]["policy"]
                    new_register.fields = self._parse_fields(registers[item]["fields"])
                    registers_list.append(new_register)
            else:
                new_register = register.Register()
                new_register.name = item
                new_register.offset = int(registers[item]["offset"])
                new_register.policy = registers[item]["policy"]
                new_register.fields = self._parse_fields(registers[item]["fields"])
                registers_list.append(new_register)
        return registers_list

    def _parse_fields(self, fields):
        fields_list = []
        for item in fields:
            new_field = field.Field()
            new_field.name = item
            new_field.position = int(fields[item]["position"])
            new_field.mask = fields[item]["mask"]
            new_field.policy = fields[item]["policy"]
            fields_list.append(new_field)
        return fields_list

    def parse(self, reg_file):
        peripherals = {}
        self._get_peripherals(reg_file, peripherals)
        parsed_peripherals_list = self._parse_peripherals(peripherals)
        return parsed_peripherals_list

