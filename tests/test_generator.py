import pytest
import yaml
import importlib.resources as resources
from pathlib import Path

import dral


class TestDralGenerator:

    def get_svd_file(self, brand, chip):
        with resources.path("dral.devices.%s" % brand, "%s.svd" % chip) as svd:
            return Path(svd)

    @pytest.mark.parametrize("device", ["stm32.f4.stm32f411", "stm32.f4.stm32f446"])
    @pytest.mark.parametrize("template", ["default"])
    def test_supported_svd_devices(self, device: str, template: str, datadir: Path):
        svd = device.split(".")
        svd_path = self.get_svd_file("%s.%s" % (svd[0], svd[1]), svd[2])
        adapter = dral.adapter.SvdAdapter(svd_path)
        device_data = adapter.convert()
        generator = dral.Generator(template=template)
        objects = generator.generate(device_data)

        with open(datadir / "generator" / template / f"{device.replace('.', '_')}.yaml") as data:
            expected_output = yaml.load(data, Loader=yaml.FullLoader)

        assert objects == expected_output
