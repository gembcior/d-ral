from __future__ import annotations

import json
from pathlib import Path

import pytest

from dral.adapter import SvdAdapter


class TestDralAdapter:
    @pytest.mark.parametrize("svd", ["arm_example"])
    def test_svd_adapter(self, svd: str, datadir: Path):
        svd_path = datadir / "svd" / f"{svd}.svd"
        adapter = SvdAdapter()
        dral_device = adapter.convert(svd_path)

        # with open(datadir / "adapter" / f"{svd}.json", "w", encoding="utf-8") as data:
        #     data.write(json.dumps(dral_device.asdict(), indent=4))

        with open(datadir / "adapter" / f"{svd}.json", encoding="utf-8") as data:
            expected_dral_device = json.loads(data.read())

        assert dral_device.asdict() == expected_dral_device
