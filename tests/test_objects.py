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

from dral.core.objects import (
    DralAccessType,
    DralDevice,
    DralField,
    DralGroup,
    DralGroupInstance,
    DralParentObject,
    DralRegister,
)

RW = DralAccessType.ReadWrite
RO = DralAccessType.ReadOnly
WO = DralAccessType.WriteOnly
UINT32 = "uint32_t"


# ---------------------------------------------------------------------------
# DralField
# ---------------------------------------------------------------------------


class TestDralField:
    def test_basic_construction(self) -> None:
        f = DralField(name="DP", position=0, width=1, access=RW, value_type=UINT32)
        assert f.name == "DP"
        assert f.position == 0
        assert f.width == 1
        assert f.access == RW
        assert f.value_type == UINT32

    def test_dral_object_is_class_name(self) -> None:
        f = DralField(name="X", position=0, width=1, access=RW, value_type=UINT32)
        assert f.dral_object == "DralField"

    def test_link_parent_sets_parent(self) -> None:
        f = DralField(name="X", position=0, width=1, access=RW, value_type=UINT32)
        parents = [DralParentObject(name="Reg", address=0)]
        f.link_parent(parents)
        assert f.parent == parents

    def test_link_parent_none_clears_parent(self) -> None:
        f = DralField(name="X", position=0, width=1, access=RW, value_type=UINT32)
        f.link_parent(None)
        assert f.parent == []

    def test_asdict_contains_all_fields(self) -> None:
        field_position = 2
        field_width = 4
        f = DralField(name="X", position=field_position, width=field_width, access=RO, value_type=UINT32)
        d = f.asdict()
        assert d["name"] == "X"
        assert d["position"] == field_position
        assert d["width"] == field_width

    def test_flat_returns_copy(self) -> None:
        f = DralField(name="X", position=0, width=1, access=RW, value_type=UINT32)
        copy = f.flat()
        assert copy == f
        assert copy is not f


# ---------------------------------------------------------------------------
# DralRegister
# ---------------------------------------------------------------------------


class TestDralRegister:
    def test_basic_construction(self) -> None:
        register_address = 0x10
        register_size = 32
        r = DralRegister(name="Apple", address=register_address, size=register_size, access=RW, value_type=UINT32)
        assert r.name == "Apple"
        assert r.address == register_address
        assert r.size == register_size
        assert r.fields == []

    def test_dral_object_is_class_name(self) -> None:
        r = DralRegister(name="R", address=0, size=32, access=RW, value_type=UINT32)
        assert r.dral_object == "DralRegister"

    def test_reset_value_propagates_to_fields(self) -> None:
        # reset_value=0b1011 (11), field at position 0 width 4 → should get 0b1011 = 11
        # field at position 0 width 2 → (11 >> 0) & 0b11 = 3
        reset_val = 0b11
        f = DralField(name="F", position=0, width=2, access=RW, value_type=UINT32)
        r = DralRegister(name="R", address=0, size=32, access=RW, value_type=UINT32, fields=[f], reset_value=reset_val)
        assert r.fields[0].reset_value == reset_val

    def test_link_parent_sets_parent_and_propagates_to_fields(self) -> None:
        f = DralField(name="F", position=0, width=1, access=RW, value_type=UINT32)
        r = DralRegister(name="R", address=0x100, size=32, access=RW, value_type=UINT32, fields=[f])
        parents = [DralParentObject(name="Dev", address=0)]
        r.link_parent(parents)
        assert r.parent == parents
        # The field's parent chain should include the register
        assert any(p.name == "R" for p in r.fields[0].parent)

    def test_asdict_includes_fields(self) -> None:
        f = DralField(name="F", position=0, width=1, access=RW, value_type=UINT32)
        r = DralRegister(name="R", address=0, size=32, access=RW, value_type=UINT32, fields=[f])
        d = r.asdict()
        assert len(d["fields"]) == 1
        assert d["fields"][0]["name"] == "F"


# ---------------------------------------------------------------------------
# DralGroup
# ---------------------------------------------------------------------------


class TestDralGroup:
    def _make_group(self, name: str = "G", address: int = 0, registers: list[DralRegister] | None = None) -> DralGroup:
        return DralGroup(
            name=name,
            address=address,
            offset=0,
            instances=[DralGroupInstance(name=name, address=address)],
            groups=[],
            registers=registers or [],
        )

    def test_basic_construction(self) -> None:
        group_address = 0x1000
        g = self._make_group("G", group_address)
        assert g.name == "G"
        assert g.address == group_address

    def test_dral_object_is_class_name(self) -> None:
        g = self._make_group()
        assert g.dral_object == "DralGroup"

    def test_link_parent_propagates_to_registers(self) -> None:
        r = DralRegister(name="R", address=0, size=32, access=RW, value_type=UINT32)
        g = DralGroup(
            name="G",
            address=0x1000,
            offset=0,
            instances=[DralGroupInstance(name="G", address=0x1000)],
            groups=[],
            registers=[r],
        )
        parents = [DralParentObject(name="Dev", address=0)]
        g.link_parent(parents)
        # Register's parent chain should contain the group
        assert any(p.name == "G" for p in r.parent)

    def test_flat_with_instances_produces_one_group_per_instance(self) -> None:
        r = DralRegister(name="Ctrl", address=0, size=32, access=RW, value_type=UINT32)
        g = DralGroup(
            name="Port_x",
            address=0x1000,
            offset=0x1000,
            instances=[
                DralGroupInstance(name="Port_0", address=0x1000),
                DralGroupInstance(name="Port_1", address=0x2000),
            ],
            groups=[],
            registers=[r],
        )
        result = g.flat()
        expected_instance_count = 2
        assert len(result) == expected_instance_count
        names = {grp.registers[0].name for grp in result}
        assert "Port_0_Ctrl" in names
        assert "Port_1_Ctrl" in names

    def test_collect_registers_includes_subgroup_registers(self) -> None:
        sub_reg = DralRegister(name="Sub", address=0x10, size=32, access=RW, value_type=UINT32)
        sub_group = DralGroup(
            name="Sub_x",
            address=0x100,
            offset=0x100,
            instances=[DralGroupInstance(name="Sub_0", address=0x100)],
            groups=[],
            registers=[sub_reg],
        )
        top_reg = DralRegister(name="Top", address=0x00, size=32, access=RW, value_type=UINT32)
        top_group = DralGroup(
            name="Top_x", address=0, offset=0, instances=[DralGroupInstance(name="Top_0", address=0)], groups=[sub_group], registers=[top_reg]
        )
        collected = top_group._collect_registers()
        names = {r.name for r in collected}
        assert "Top" in names
        assert "Sub_0_Sub" in names


# ---------------------------------------------------------------------------
# DralDevice
# ---------------------------------------------------------------------------


class TestDralDevice:
    def test_basic_construction(self) -> None:
        d = DralDevice(name="Dev")
        assert d.name == "Dev"
        assert d.groups == []
        assert d.address == 0

    def test_dral_object_is_class_name(self) -> None:
        d = DralDevice(name="Dev")
        assert d.dral_object == "DralDevice"

    def test_link_parent_is_called_on_init(self) -> None:
        r = DralRegister(name="R", address=0, size=32, access=RW, value_type=UINT32)
        g = DralGroup(name="G", address=0, offset=0, instances=[DralGroupInstance(name="G", address=0)], groups=[], registers=[r])
        DralDevice(name="Dev", groups=[g])
        # The register should have at least one parent entry from the device + group
        assert len(r.parent) >= 1

    def test_flat_produces_single_group_with_all_registers(self) -> None:
        r1 = DralRegister(name="R1", address=0x10, size=32, access=RW, value_type=UINT32)
        r2 = DralRegister(name="R2", address=0x20, size=32, access=RW, value_type=UINT32)
        g1 = DralGroup(name="A", address=0x10, offset=0, instances=[DralGroupInstance(name="A", address=0x10)], groups=[], registers=[r1])
        g2 = DralGroup(name="B", address=0x20, offset=0, instances=[DralGroupInstance(name="B", address=0x20)], groups=[], registers=[r2])
        d = DralDevice(name="Dev", groups=[g1, g2])
        flat = d.flat()
        expected_group_count = 1
        expected_register_count = 2
        assert len(flat.groups) == expected_group_count
        assert len(flat.groups[0].registers) == expected_register_count

    def test_sort_orders_groups_and_registers(self) -> None:
        first_address = 0x10
        r_b = DralRegister(name="B", address=0x20, size=32, access=RW, value_type=UINT32)
        r_a = DralRegister(name="A", address=first_address, size=32, access=RW, value_type=UINT32)
        g = DralGroup(name="G", address=0, offset=0, instances=[], groups=[], registers=[r_b, r_a])
        d = DralDevice(name="Dev", groups=[g])
        d.sort()
        assert d.groups[0].registers[0].address == first_address

    def test_asdict_round_trip(self) -> None:
        d = DralDevice(name="Dev")
        result = d.asdict()
        assert result["name"] == "Dev"
        assert result["dral_object"] == "DralDevice"
