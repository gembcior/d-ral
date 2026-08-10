from __future__ import annotations

import json
from pathlib import Path

import pytest

from dral.adapter import SvdAdapter
from dral.adapter.svd import IncorrectSvdError


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

    def test_svd_adapter_resolves_cross_scope_derived_from(self, datadir: Path):
        # Previously impossible: dral's own resolver rejected any dotted,
        # cross-scope derivedFrom with NotImplementedError. Now resolved
        # upstream by svd2py before dral even sees the parsed data.
        svd_path = datadir / "svd" / "cross_scope_derived.svd"
        adapter = SvdAdapter()
        dral_device = adapter.convert(svd_path)

        groups = {group.name: group for group in dral_device.groups}
        reg_y = next(register for register in groups["PeripheralB"].registers if register.name == "RegY")

        # Inherited wholesale from PeripheralA.RegX (not redefined by RegY).
        assert reg_y.size == 32
        assert reg_y.access == groups["PeripheralA"].registers[0].access
        assert len(reg_y.fields) == 1
        assert reg_y.fields[0].name == "FieldX"
        assert reg_y.fields[0].width == 4

        # Own values override the inherited ones.
        assert reg_y.description == "Cross-scope derived register"
        assert reg_y.address == 0x4

    def test_svd_adapter_wraps_unresolvable_derived_from(self, tmp_path: Path):
        bad_svd = tmp_path / "bad.svd"
        bad_svd.write_text("""
            <device schemaVersion="1.3">
              <name>BadDevice</name>
              <peripherals>
                <peripheral>
                  <name>PeriphA</name>
                  <baseAddress>0x40000000</baseAddress>
                  <registers>
                    <register derivedFrom="DoesNotExist">
                      <name>RegA</name>
                      <addressOffset>0x0</addressOffset>
                    </register>
                  </registers>
                </peripheral>
              </peripherals>
            </device>
        """)
        adapter = SvdAdapter()

        with pytest.raises(IncorrectSvdError, match="DoesNotExist"):
            adapter.convert(bad_svd)
