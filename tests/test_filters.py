# =================================================================================
#
# MIT License
#
# Copyright (c) 2026 Gembcior
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# =================================================================================

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

        with open(datadir / "filters" / "groups" / f"{svd}.json", encoding="utf-8") as data:
            expected_dral_device = json.loads(data.read())

        assert dral_device.asdict() == expected_dral_device
