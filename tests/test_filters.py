from __future__ import annotations

import importlib.resources as resources
from pathlib import Path
from typing import Dict

import pytest
import yaml

from dral.adapter import SvdAdapter, WhiteBlackListAdapter
from dral.filter import WhiteListFilter
from dral.types import Device, Field, Peripheral, Register


class TestDralFilters:
    def get_svd_file(self, brand, chip):
        with resources.path("dral.devices.%s" % brand, "%s.svd" % chip) as svd:
            return Path(svd)

    @pytest.fixture
    def wldir(self, datadir):
        return datadir / "filters" / "white_list"

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
            reset_value=data["reset_value"],
            fields=[self.create_field_object(field) for field in data["fields"]],
        )

    def create_field_object(self, data: Dict) -> Field:
        return Field(
            name=data["name"],
            description=data["description"],
            position=data["position"],
            width=data["width"],
        )

    @pytest.mark.parametrize("device", ["arm.example.example1"])
    @pytest.mark.parametrize("white_list", ["arm.example.wl1", "arm.example.wl2", "arm.example.wl3", "arm.example.wl4"])
    def test_white_list_filter(self, device, white_list, wldir):
        svd = device.split(".")
        svd_path = self.get_svd_file(f"{svd[0]}.{svd[1]}", svd[2])
        dral = SvdAdapter(svd_path).convert()

        wl = WhiteBlackListAdapter(wldir / "input" / f"{white_list}.yaml").convert()
        wl_filter = WhiteListFilter(wl)

        with open(wldir / "expected" / f"{white_list}.yaml") as data:
            expected_output = yaml.load(data, Loader=yaml.FullLoader)
        expected_device = self.create_device_object(expected_output)

        result = wl_filter.apply(dral)

        assert result == expected_device
