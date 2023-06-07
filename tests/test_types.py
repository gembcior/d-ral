from __future__ import annotations

import pytest
import yaml

import dral


class TestDralTypes:
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

    @pytest.fixture
    def test_devices(self, datadir):
        test_devices_file = datadir / "types" / "devices.yaml"
        with open(test_devices_file, "r") as test_devices:
            devices = yaml.load(test_devices, Loader=yaml.FullLoader)
        return devices

    @pytest.mark.parametrize("field", ["field0", "field1"])
    def test_field_type_creation(self, field, test_fields):
        test_field = test_fields[field]
        field = dral.Field(**test_field)

        assert field.name == test_field["name"]
        assert field.description == test_field["description"]
        assert field.position == test_field["position"]
        assert field.width == test_field["width"]
        assert field.mask == ((1 << test_field["width"]) - 1)

    @pytest.mark.parametrize(
        "field_a",
        [
            "field0",
            "field1",
        ],
    )
    @pytest.mark.parametrize(
        "field_b",
        [
            "field0",
            "field1",
        ],
    )
    def test_field_type_comparison(self, field_a, field_b, test_fields):
        test_field_a = dral.Field(**test_fields[field_a])
        test_field_b = dral.Field(**test_fields[field_b])

        if field_a == field_b:
            assert test_field_a == test_field_b
        else:
            assert test_field_a != test_field_b

    @pytest.mark.parametrize("register", ["register0", "register1"])
    def test_register_type_creation(self, register, test_registers):
        test_register = test_registers[register]
        register = dral.Register(**test_register)

        assert register.name == test_register["name"]
        assert register.description == test_register["description"]
        assert register.offset == test_register["offset"]
        assert register.size == test_register["size"]
        assert register.access == test_register["access"]
        assert register.reset_value == test_register["reset_value"]

    @pytest.mark.parametrize(
        "register_a",
        [
            "register0",
            "register1",
        ],
    )
    @pytest.mark.parametrize(
        "register_b",
        [
            "register0",
            "register1",
        ],
    )
    def test_register_type_comparison(self, register_a, register_b, test_registers):
        test_register_a = dral.Register(**test_registers[register_a])
        test_register_b = dral.Register(**test_registers[register_b])

        if register_a == register_b:
            assert test_register_a == test_register_b
        else:
            assert test_register_a != test_register_b

    @pytest.mark.parametrize("peripheral", ["peripheral0", "peripheral1"])
    def test_peripheral_type_creation(self, peripheral, test_peripherals):
        test_peripheral = test_peripherals[peripheral]
        peripheral = dral.Peripheral(**test_peripheral)

        assert peripheral.name == test_peripheral["name"]

    @pytest.mark.parametrize(
        "peripheral_a",
        [
            "peripheral0",
            "peripheral1",
        ],
    )
    @pytest.mark.parametrize(
        "peripheral_b",
        [
            "peripheral0",
            "peripheral1",
        ],
    )
    def test_peripheral_type_comparison(self, peripheral_a, peripheral_b, test_peripherals):
        test_peripheral_a = dral.Peripheral(**test_peripherals[peripheral_a])
        test_peripheral_b = dral.Peripheral(**test_peripherals[peripheral_b])

        if peripheral_a == peripheral_b:
            assert test_peripheral_a == test_peripheral_b
        else:
            assert test_peripheral_a != test_peripheral_b

    @pytest.mark.parametrize("device", ["device0", "device1"])
    def test_device_type_creation(self, device, test_devices):
        test_device = test_devices[device]
        device = dral.Device(**test_device)

        assert device.name == test_device["name"]

    @pytest.mark.parametrize(
        "device_a",
        [
            "device0",
            "device1",
        ],
    )
    @pytest.mark.parametrize(
        "device_b",
        [
            "device0",
            "device1",
        ],
    )
    def test_device_type_comparison(self, device_a, device_b, test_devices):
        test_device_a = dral.Device(**test_devices[device_a])
        test_device_b = dral.Device(**test_devices[device_b])

        if device_a == device_b:
            assert test_device_a == test_device_b
        else:
            assert test_device_a != test_device_b
