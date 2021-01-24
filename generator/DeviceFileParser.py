import Device as device
import Peripheral as peripheral
import Register as register
import Field as field
import yaml
import os
import re


class DeviceFileParser:
    def __init__(self):
        pass

    def _get_device_data(self, device_file, device_data):
        with open(device_file, "r") as yaml_file:
            yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
            device_data.peripherals.update(yaml_data["peripherals"])
            if "brand" in yaml_data:
                device_data.brand = yaml_data["brand"]
            if "family" in yaml_data:
                device_data.family = yaml_data["family"]
            if "chip" in yaml_data:
                device_data.chip = yaml_data["chip"]

        include_file_list = []
        with open(device_file, "r") as yaml_file:
            include_file_pattern = re.compile('"(.*?)"')
            for line in yaml_file.readlines():
                if line.startswith("#include"):
                    include_file_list.append(os.path.join(os.path.dirname(device_file), re.findall(include_file_pattern, line)[0]))

        for include_file in include_file_list:
            self._get_device_data(include_file, device_data)

    def _parse_peripherals(self, peripherals):
        peripherals_list = []
        for item in peripherals:
            peripheral_type = peripherals[item]["type"]
            if peripheral_type == "collection":
                collection = peripherals[item]["collection"]
                for element in collection:
                    new_peripheral = peripheral.PeripheralCollection()
                    new_peripheral.name = "%s%s" % (item, element)
                    new_peripheral.type = peripheral_type
                    new_peripheral.address = collection[element]["address"]
                    new_peripheral.registers = self._parse_registers(peripherals[item]["registers"])
                    peripherals_list.append(new_peripheral)
            else:
                new_peripheral = peripheral.Peripheral()
                new_peripheral.name = item
                new_peripheral.type = peripheral_type
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

    def parse(self, device_file):
        device_data = device.Device()
        self._get_device_data(device_file, device_data)
        device_data.peripherals = self._parse_peripherals(device_data.peripherals)
        return device_data

