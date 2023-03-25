from __future__ import annotations

import importlib.resources as resources
from pathlib import Path
from typing import Dict

import pytest
import yaml

from dral.adapter import SvdAdapter
from dral.types import Device, Field, Peripheral, Register


class TestDralAdapter:
    def get_svd_file(self, brand, chip):
        with resources.path("dral.devices.%s" % brand, "%s.svd" % chip) as svd:
            return Path(svd)

    def create_device_object(self, data: Dict) -> Device:
        return Device(
            name=data["name"],
            description=data["description"],
            peripherals=[self.create_peripheral_object(peripheral) for peripheral in data["peripherals"]],
        )

    def create_peripheral_object(self, data: Dict) -> Peripheral:
        return Peripheral(
            name=data["name"],
            description=data["description"],
            address=data["address"],
            registers=[self.create_regiter_object(register) for register in data["registers"]],
        )

    def create_regiter_object(self, data: Dict) -> Register:
        return Register(
            name=data["name"],
            description=data["description"],
            offset=data["offset"],
            size=data["size"],
            access=data["access"],
            reset_value=data["reset_value"],
            fields=[self.create_field_object(field) for field in data["fields"]],
        )

    def create_field_object(self, data: Dict) -> Field:
        return Field(
            name=data["name"],
            description=data["description"],
            position=data["position"],
            mask=data["mask"],
            width=data["width"],
        )

    @pytest.mark.parametrize("device", ["arm.example.example1", "stm32.f4.stm32f411", "stm32.f4.stm32f446"])
    def test_svd_adapter(self, device, datadir):
        svd = device.split(".")
        svd_path = self.get_svd_file(f"{svd[0]}.{svd[1]}", svd[2])
        adapter = SvdAdapter(svd_path)
        dral = adapter.convert()

        with open(datadir / "adapter" / f"{device}.yaml") as data:
            expected_output = yaml.load(data, Loader=yaml.FullLoader)
        expected_device = self.create_device_object(expected_output)

        assert dral == expected_device
