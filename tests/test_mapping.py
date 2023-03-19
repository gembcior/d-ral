import importlib.resources as resources
from pathlib import Path
from typing import Dict

import pytest
import yaml

import dral


class TestDralMapping:
    @pytest.fixture
    def test_fields(self, datadir):
        test_fields_file = datadir / "types" / "fields.yaml"
        with open(test_fields_file, "r") as test_fields:
            fields = yaml.load(test_fields, Loader=yaml.FullLoader)
        return fields

    @pytest.fixture
    def test_registers(self, datadir):
        test_registers_file = datadir / "types" / "registers.yaml"
        with open(test_registers_file, "r") as test_registers:
            registers = yaml.load(test_registers, Loader=yaml.FullLoader)
        return registers

    @pytest.fixture
    def test_peripherals(self, datadir):
        test_peripherals_file = datadir / "types" / "peripherals.yaml"
        with open(test_peripherals_file, "r") as test_peripherals:
            peripherals = yaml.load(test_peripherals, Loader=yaml.FullLoader)
        return peripherals

    @pytest.mark.parametrize(
        "field",
        [
            "field0",
            "field1",
        ],
    )
    @pytest.mark.parametrize("mapping", ["default"])
    def test_fields_mapping(self, field: str, mapping: str, test_fields: Dict):
        test_field = dral.Field(**test_fields[field])
        mapping_object = dral.DralMapping(mapping)
        mapping_result = mapping_object.get(test_field)
        print(mapping_result)


    @pytest.mark.parametrize(
        "register",
        [
            "register0",
            "register1",
        ],
    )
    @pytest.mark.parametrize("mapping", ["default"])
    def test_registers_mapping(self, register: str, mapping: str, test_registers: Dict):
        test_register = dral.Register(**test_registers[register])
        mapping_object = dral.DralMapping(mapping)
        mapping_result = mapping_object.get(test_register)
        print(mapping_result)
