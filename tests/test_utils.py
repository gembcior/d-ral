from pathlib import Path

import pytest

from dral.utils import Utils


class TestDralUtils:
    @pytest.mark.parametrize("template", ["dral", "mbedAutomatify"])
    def test_get_template(self, template: str, rootdir: Path):
        base_template_files = ["peripheral.dral", "register.dral", "field.dral"]
        templates_subpath = "dral/templates"
        for name in base_template_files:
            result = Utils.get_template(template, name)
            expected = rootdir.parents[0] / templates_subpath / template / name
            assert expected == result

    @pytest.mark.parametrize("device, svd", [("stm32f446", "stm32/f4/stm32f446.svd"), ("stm32f411", "stm32/f4/stm32f411.svd")])
    def test_get_svd_file(self, device: str, svd: str, rootdir: Path):
        result = Utils.get_svd_file(device)
        device_subpath = "dral/devices"
        expected = rootdir.parents[0] / device_subpath / svd
        assert expected == result

    @pytest.mark.parametrize("chip, family, brand", [("stm32f446", "f4", "stm32"), ("stm32f411", "f4", "stm32")])
    def test_get_device_info(self, chip: str, family: str, brand: str):
        svd = Utils.get_svd_file(chip)
        assert svd is not None
        result = Utils.get_device_info(svd)
        assert result[0] == chip
        assert result[1] == family
        assert result[2] == brand
