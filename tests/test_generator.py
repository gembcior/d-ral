from __future__ import annotations

import importlib.resources as resources
from pathlib import Path

import pytest
import yaml

import dral


class TestDralGenerator:
    def get_svd_file(self, brand, chip):
        with resources.path("dral.devices.%s" % brand, "%s.svd" % chip) as svd:
            return Path(svd)

    def get_template_dir(self, name: str) -> Path:
        with resources.path(f"dral.templates.{name}", "__init__.py") as svd:
            return Path(svd).parent

    @pytest.mark.parametrize("device", ["arm.example.example1", "stm32.f4.stm32f411", "stm32.f4.stm32f446"])
    @pytest.mark.parametrize("template", ["dral"])
    def test_supported_svd_devices(self, device: str, template: str, datadir: Path):
        svd = device.split(".")
        svd_path = self.get_svd_file(f"{svd[0]}.{svd[1]}", svd[2])
        adapter = dral.adapter.SvdAdapter(svd_path)
        device_data = adapter.convert()
        device_data = dral.filter.BanksFilter().apply(device_data)
        template_dir = self.get_template_dir(template)
        template_object = dral.DralTemplate(template_dir)
        with open(datadir / "generator" / template / "mapping.yaml", "r", encoding="utf-8") as mapping_file:
            mapping = yaml.load(mapping_file, Loader=yaml.FullLoader)
        generator = dral.DralGenerator(template=template_object)
        objects = generator.generate(device_data, mapping=mapping)

        with open(datadir / "generator" / template / f"{device}.yaml") as data:
            expected_output = []
            for item in yaml.load(data, Loader=yaml.FullLoader):
                expected_output.append(dral.DralOutputFile(item["name"], item["content"]))

        assert objects == expected_output
