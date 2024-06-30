from __future__ import annotations

import json
from pathlib import Path

import pytest

from dral.adapter import SvdAdapter
from dral.filter.groups import GroupsFilter


class TestDralFilters:

    @pytest.mark.parametrize("svd", ["arm_example"])
    def test_groups_filter(self, svd: str, datadir: Path):
        svd_path = datadir / "svd" / f"{svd}.svd"
        adapter = SvdAdapter()
        dral_device = adapter.convert(svd_path)
        filter = GroupsFilter()
        dral_device = filter.apply(dral_device)

        # with open(datadir / "filters" / "groups" / f"{svd}.json", "w", encoding="utf-8") as data:
        #     data.write(json.dumps(dral_device.asdict(), indent=4))

        with open(datadir / "filters" / "groups" / f"{svd}.json", "r", encoding="utf-8") as data:
            expected_dral_device = json.loads(data.read())

        assert dral_device.asdict() == expected_dral_device
