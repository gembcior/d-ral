import yaml
import os
import re
from Device import Device
from Peripheral import Peripheral
from Collection import Collection, CollectionInstance
from Register import Register
from Register import CollectionRegister
from Field import Field
from RegisterModel import RegisterModel


class DeviceFileParser:
    def __init__(self):
        self._device = None

    def _parse_device_file(self, device_file):
        with open(device_file, "r") as yaml_file:
            yaml_data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        self._parse_yaml_data(yaml_data)
        include_file_list = self._parse_include_files(device_file)
        for include_file in include_file_list:
            self._parse_device_file(include_file)

    def _parse_include_files(self, device_file):
        include_file_list = []
        with open(device_file, "r") as yaml_file:
            include_file_pattern = re.compile('"(.*?)"')
            for line in yaml_file.readlines():
                if line.startswith("#include"):
                    include_file_list.append(os.path.join(os.path.dirname(device_file), re.findall(include_file_pattern, line)[0]))
        return include_file_list

    def _parse_yaml_data(self, data):
        if "peripherals" in data:
            self._device.peripherals += self._parse_peripherals(data["peripherals"])

        if "brand" in data:
            self._device.brand = data["brand"]

        if "family" in data:
            self._device.family = data["family"]

        if "chip" in data:
            self._device.chip = data["chip"]

        if "model" in data:
            new_model = RegisterModel()
            new_model.name = data["model"] + "_model"
            self._device.model = new_model
        else:
            new_model = RegisterModel()
            new_model.name = "default_model"
            self._device.model = new_model

    def _parse_peripherals(self, peripherals):
        peripherals_list = []
        for item in peripherals:
            peripheral_type = peripherals[item]["type"]
            if peripheral_type == "collection":
                collection = peripherals[item]["collection"]
                new_peripheral = Collection()
                new_peripheral.name = item
                new_peripheral.type = peripheral_type
                new_peripheral.registers = self._parse_collection_registers(peripherals[item]["registers"])
                new_peripheral.instances = self._parse_collection(peripherals[item]["collection"])
                peripherals_list.append(new_peripheral)
            else:
                new_peripheral = Peripheral()
                new_peripheral.name = item
                new_peripheral.type = peripheral_type
                new_peripheral.address = int(peripherals[item]["address"])
                new_peripheral.registers = self._parse_registers(peripherals[item]["registers"])
                peripherals_list.append(new_peripheral)
        return peripherals_list

    def _parse_collection(self, collection):
        collection_list = []
        for item in collection:
            new_collection = CollectionInstance()
            new_collection.name = item
            new_collection.address = int(collection[item]["address"])
            collection_list.append(new_collection)
        return collection_list

    def _parse_registers(self, registers):
        registers_list = []
        for item in registers:
            if "range" in registers[item]:
                start = int(registers[item]["range"]["start"])
                end = int(registers[item]["range"]["end"])
                for num in range(start, end + 1):
                    new_register = Register()
                    new_register.name = "%s%d" % (item, num)
                    new_register.offset = int(registers[item]["offset"] + (0x04 * num))
                    new_register.policy = registers[item]["policy"]
                    new_register.fields = self._parse_fields(registers[item]["fields"])
                    registers_list.append(new_register)
            else:
                new_register = Register()
                new_register.name = item
                new_register.offset = int(registers[item]["offset"])
                new_register.policy = registers[item]["policy"]
                new_register.fields = self._parse_fields(registers[item]["fields"])
                registers_list.append(new_register)
        return registers_list

    def _parse_collection_registers(self, registers):
        registers_list = []
        for item in registers:
            if "range" in registers[item]:
                start = int(registers[item]["range"]["start"])
                end = int(registers[item]["range"]["end"])
                for num in range(start, end + 1):
                    new_register = CollectionRegister()
                    new_register.name = "%s%d" % (item, num)
                    new_register.offset = int(registers[item]["offset"] + (0x04 * num))
                    new_register.policy = registers[item]["policy"]
                    new_register.fields = self._parse_fields(registers[item]["fields"])
                    registers_list.append(new_register)
            else:
                new_register = CollectionRegister()
                new_register.name = item
                new_register.offset = int(registers[item]["offset"])
                new_register.policy = registers[item]["policy"]
                new_register.fields = self._parse_fields(registers[item]["fields"])
                registers_list.append(new_register)
        return registers_list

    def _parse_fields(self, fields):
        fields_list = []
        for item in fields:
            new_field = Field()
            new_field.name = item
            new_field.position = int(fields[item]["position"])
            new_field.mask = fields[item]["mask"]
            new_field.policy = fields[item]["policy"]
            fields_list.append(new_field)
        return fields_list

    def parse(self, device_file):
        self._device = Device()
        self._parse_device_file(device_file)
        return self._device

