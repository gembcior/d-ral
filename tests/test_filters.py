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
from unittest.mock import MagicMock

import pytest

from dral.adapter import SvdAdapter
from dral.core.objects import (
    DralAccessType,
    DralDevice,
    DralField,
    DralGroup,
    DralGroupInstance,
    DralRegister,
)
from dral.filter.flat import FlatFilter
from dral.filter.groups import GroupsFilter
from dral.filter.supervisor import FilterSupervisor

RW = DralAccessType.ReadWrite
RO = DralAccessType.ReadOnly
UINT32 = "uint32_t"

STRIDE_0X100 = 0x100
THREE_INSTANCES = 3
TWO_INSTANCES = 2
STRIDE_0X1000 = 0x1000


def _multi_instance_group() -> DralGroup:
    """A group with two instances and one register per instance."""
    return DralGroup(
        name="Port_x",
        description="Multi-instance port",
        address=0x1000,
        offset=0x1000,
        instances=[
            DralGroupInstance(name="Port_0", address=0x1000),
            DralGroupInstance(name="Port_1", address=0x2000),
        ],
        groups=[],
        registers=[_register("Ctrl", address=0)],
    )


def _device_with_multi_group() -> DralDevice:
    return DralDevice(name="Dev", groups=[_multi_instance_group()])


def _field(name: str, position: int = 0, width: int = 8, access: DralAccessType = RW) -> DralField:
    return DralField(name=name, position=position, width=width, access=access, value_type=UINT32)


def _register(name: str, address: int = 0, fields: list[DralField] | None = None) -> DralRegister:
    return DralRegister(name=name, address=address, size=32, access=RW, value_type=UINT32, fields=fields or [])


def _group(name: str, address: int = 0, registers: list[DralRegister] | None = None, groups: list[DralGroup] | None = None) -> DralGroup:
    return DralGroup(
        name=name,
        address=address,
        offset=0,
        instances=[DralGroupInstance(name=name, address=address)],
        registers=registers or [],
        groups=groups or [],
    )


def _device(groups: list[DralGroup]) -> DralDevice:
    return DralDevice(name="TestDevice", groups=groups)


class TestDralFilters:
    @pytest.mark.parametrize("svd", ["arm_example"])
    def test_groups_filter(self, svd: str, datadir: Path) -> None:
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


class TestFlatFilter:
    def test_flat_collapses_multi_instance_group(self) -> None:
        device = _device_with_multi_group()
        result = FlatFilter().apply(device)

        assert len(result.groups) == 1
        flat_group = result.groups[0]
        # After flattening there should be no nested instances
        assert flat_group.instances == []
        assert flat_group.groups == []
        # One register per original instance, prefixed with instance name
        expected_register_count = 2
        assert len(flat_group.registers) == expected_register_count
        names = {r.name for r in flat_group.registers}
        assert "Port_0_Ctrl" in names
        assert "Port_1_Ctrl" in names

    def test_flat_preserves_device_name(self) -> None:
        device = _device_with_multi_group()
        result = FlatFilter().apply(device)
        assert result.name == "Dev"

    def test_flat_sorts_registers_by_address(self) -> None:
        group = DralGroup(
            name="G_x",
            address=0,
            offset=0x100,
            instances=[
                DralGroupInstance(name="G_1", address=0x200),
                DralGroupInstance(name="G_0", address=0x100),
            ],
            groups=[],
            registers=[_register("Reg", address=0)],
        )
        device = DralDevice(name="Dev", groups=[group])
        result = FlatFilter().apply(device)
        addrs = [r.address for r in result.groups[0].registers]
        assert addrs == sorted(addrs)


class TestFilterSupervisor:
    def test_empty_supervisor_returns_device_unchanged(self) -> None:
        device = _device_with_multi_group()
        result = FilterSupervisor().apply(device)
        assert result is device

    def test_single_filter_is_applied(self) -> None:
        device = _device_with_multi_group()
        result = FilterSupervisor(filters=[FlatFilter()]).apply(device)
        # flat filter was applied — instances are gone
        assert result.groups[0].instances == []

    def test_filters_are_applied_in_order(self) -> None:
        """Verify filters are chained: output of first feeds second."""
        call_order: list[str] = []

        class RecordingFilter:
            def __init__(self, tag: str) -> None:
                self._tag = tag

            def apply(self, device: DralDevice) -> DralDevice:
                call_order.append(self._tag)
                return device

        sup = FilterSupervisor(filters=[RecordingFilter("a"), RecordingFilter("b")])  # type: ignore[list-item]
        sup.apply(_device_with_multi_group())
        assert call_order == ["a", "b"]

    def test_add_appends_filter(self) -> None:
        sup = FilterSupervisor()
        mock = MagicMock()
        mock.apply.return_value = _device_with_multi_group()
        sup.add(mock)  # type: ignore[arg-type]
        sup.apply(_device_with_multi_group())
        mock.apply.assert_called_once()

    def test_none_filters_defaults_to_empty(self) -> None:
        sup = FilterSupervisor(filters=None)
        assert sup._filters == []


class TestCompareFields:
    def test_identical_fields_are_equal(self) -> None:
        f = _field("DP", position=0, width=1)
        filt = GroupsFilter()
        assert filt._compare_fields(f, f) is True

    def test_different_name_is_not_equal(self) -> None:
        filt = GroupsFilter()
        assert filt._compare_fields(_field("DP", 0, 1), _field("HDMI", 0, 1)) is False

    def test_different_position_is_not_equal(self) -> None:
        filt = GroupsFilter()
        assert filt._compare_fields(_field("DP", 0, 1), _field("DP", 1, 1)) is False

    def test_different_width_is_not_equal(self) -> None:
        filt = GroupsFilter()
        assert filt._compare_fields(_field("DP", 0, 1), _field("DP", 0, 4)) is False

    def test_different_access_is_not_equal(self) -> None:
        filt = GroupsFilter()
        assert filt._compare_fields(_field("DP", 0, 1, RW), _field("DP", 0, 1, RO)) is False


# ---------------------------------------------------------------------------
# Tests for _has_the_same_fields
# ---------------------------------------------------------------------------


class TestHasTheSameFields:
    def test_same_fields_returns_true(self) -> None:
        f1 = _field("DP", 0, 1)
        f2 = _field("HDMI", 2, 4)
        reg_a = _register("Apple", fields=[f1, f2])
        reg_b = _register("Apple", fields=[_field("DP", 0, 1), _field("HDMI", 2, 4)])
        filt = GroupsFilter()
        assert filt._has_the_same_fields(reg_a, reg_b) is True

    def test_different_fields_returns_false(self) -> None:
        reg_a = _register("Apple", fields=[_field("DP", 0, 1)])
        reg_b = _register("Apple", fields=[_field("USB", 0, 1)])
        filt = GroupsFilter()
        assert filt._has_the_same_fields(reg_a, reg_b) is False

    def test_extra_field_returns_false(self) -> None:
        reg_a = _register("Apple", fields=[_field("DP", 0, 1), _field("HDMI", 2, 4)])
        reg_b = _register("Apple", fields=[_field("DP", 0, 1)])
        filt = GroupsFilter()
        assert filt._has_the_same_fields(reg_a, reg_b) is False


# ---------------------------------------------------------------------------
# Tests for _compare_registers
# ---------------------------------------------------------------------------


class TestCompareRegisters:
    def test_similar_name_same_fields_is_equal(self) -> None:
        fields = [_field("DP", 0, 1)]
        reg_a = _register("Bear_0", fields=fields)
        reg_b = _register("Bear_1", fields=[_field("DP", 0, 1)])
        filt = GroupsFilter()
        assert filt._compare_registers(reg_a, reg_b) is True

    def test_completely_different_names_not_similar(self) -> None:
        fields = [_field("DP", 0, 1)]
        reg_a = _register("Apple", fields=fields)
        reg_b = _register("Banana", fields=[_field("DP", 0, 1)])
        filt = GroupsFilter()
        # Apple vs Banana - not similar names, so compare should fail
        assert filt._compare_registers(reg_a, reg_b) is False

    def test_different_access_type_not_equal(self) -> None:
        fields = [_field("DP", 0, 1)]
        reg_a = DralRegister(name="Bear_0", address=0, size=32, access=RW, value_type=UINT32, fields=fields)
        reg_b = DralRegister(name="Bear_1", address=0, size=32, access=RO, value_type=UINT32, fields=[_field("DP", 0, 1)])
        filt = GroupsFilter()
        assert filt._compare_registers(reg_a, reg_b) is False


# ---------------------------------------------------------------------------
# Tests for _get_group_offset
# ---------------------------------------------------------------------------


class TestGetGroupOffset:
    def test_uniform_stride_returns_scalar(self) -> None:
        filt = GroupsFilter()
        # offsets 0x100, 0x200, 0x300 → stride 0x100
        assert filt._get_group_offset([STRIDE_0X100, 0x200, 0x300]) == STRIDE_0X100

    def test_non_uniform_stride_returns_list_of_relative_offsets(self) -> None:
        filt = GroupsFilter()
        # offsets 0x100, 0x300, 0x800 → non-uniform → relative to first
        result = filt._get_group_offset([0x100, 0x300, 0x800])
        assert isinstance(result, list)
        assert result == [0, 0x200, 0x700]


# ---------------------------------------------------------------------------
# Tests for _all_have_similar_names
# ---------------------------------------------------------------------------


class TestAllHaveSimilarNames:
    def test_numbered_variants_are_similar(self) -> None:
        filt = GroupsFilter()
        regs = [_register("Bear_0"), _register("Bear_1"), _register("Bear_2")]
        assert filt._all_have_similar_names(regs) is True

    def test_completely_different_names_not_all_similar(self) -> None:
        filt = GroupsFilter()
        regs = [_register("Apple"), _register("Banana"), _register("Cherry")]
        assert filt._all_have_similar_names(regs) is False


# ---------------------------------------------------------------------------
# Tests for _can_merge_registers
# ---------------------------------------------------------------------------


class TestCanMergeRegisters:
    def test_registers_without_fields_cannot_merge(self) -> None:
        filt = GroupsFilter()
        regs = [_register("Bear_0"), _register("Bear_1")]
        assert filt._can_merge_registers(regs) is False

    def test_registers_with_fields_and_similar_names_can_merge(self) -> None:
        filt = GroupsFilter()
        fields = [_field("DP", 0, 1)]
        regs = [_register("Bear_0", fields=fields), _register("Bear_1", fields=[_field("DP", 0, 1)])]
        assert filt._can_merge_registers(regs) is True


# ---------------------------------------------------------------------------
# Tests for _can_merge_groups
# ---------------------------------------------------------------------------


class TestCanMergeGroups:
    def test_empty_groups_cannot_merge(self) -> None:
        filt = GroupsFilter()
        groups = [_group("Alpha_0"), _group("Alpha_1")]
        # groups have no children
        assert filt._can_merge_groups(groups) is False

    def test_groups_with_registers_and_similar_names_can_merge(self) -> None:
        filt = GroupsFilter()
        regs = [_register("Bear", fields=[_field("DP", 0, 1)])]
        groups = [_group("Alpha_0", registers=regs), _group("Alpha_1", registers=[_register("Bear", fields=[_field("DP", 0, 1)])])]
        assert filt._can_merge_groups(groups) is True


# ---------------------------------------------------------------------------
# Integration tests for GroupsFilter.apply
# ---------------------------------------------------------------------------


class TestGroupsFilterApply:
    def test_no_merge_when_single_group(self) -> None:
        """A lone group should pass through unchanged."""
        group = _group("Alfa", address=0x1000, registers=[_register("Apple", fields=[_field("DP", 0, 1)])])
        device = _device([group])
        result = GroupsFilter().apply(device)
        assert len(result.groups) == 1
        assert result.groups[0].name == "Alfa"

    def test_similar_registers_are_merged_into_group(self) -> None:
        """Three similar registers with numbered names and same fields should be merged into a group."""
        fields = [_field("DP", 0, 1)]
        group = _group(
            "Bravo",
            address=0x2000,
            registers=[
                _register("Bear_0", address=0x00, fields=fields),
                _register("Bear_1", address=0x20, fields=[_field("DP", 0, 1)]),
                _register("Bear_2", address=0x40, fields=[_field("DP", 0, 1)]),
            ],
        )
        device = _device([group])
        result = GroupsFilter().apply(device)

        # The three Bear_N registers should have been merged into a nested group
        bravo = result.groups[0]
        assert bravo.name == "Bravo"
        assert len(bravo.groups) == 1
        merged = bravo.groups[0]
        assert merged.name == "Bear_x"
        assert len(merged.instances) == THREE_INSTANCES

    def test_similar_top_level_groups_are_merged(self) -> None:
        """Two identical groups with numbered names should merge into one multi-instance group."""
        regs = [_register("Apple", fields=[_field("DP", 0, 1)])]
        g0 = _group("Alpha_0", address=0x1000, registers=regs)
        g1 = _group("Alpha_1", address=0x2000, registers=[_register("Apple", fields=[_field("DP", 0, 1)])])
        device = _device([g0, g1])
        result = GroupsFilter().apply(device)
        assert len(result.groups) == 1
        merged = result.groups[0]
        assert merged.name == "Alpha_x"
        assert len(merged.instances) == TWO_INSTANCES

    def test_duplicate_name_after_merge_raises(self) -> None:
        """Two groups with the same name but different registers cannot be merged and trigger a duplicate-name error."""
        # Different registers → _compare_groups returns False → both survive → duplicate check fires
        g0 = _group("Dup", address=0x100, registers=[_register("RegA", fields=[_field("F1", 0, 1)])])
        g1 = _group("Dup", address=0x200, registers=[_register("RegB", fields=[_field("F2", 0, 1)])])
        device = DralDevice(name="Dev", groups=[g0, g1])
        with pytest.raises(ValueError, match="Duplicated groups"):
            GroupsFilter().apply(device)

    def test_uniform_stride_computed_correctly(self) -> None:
        """Merged group offset should reflect uniform stride between instances."""
        fields = [_field("X", 0, 4)]
        regs = [_register("Reg", fields=fields)]
        g0 = _group("Port_0", address=0x0000, registers=regs)
        g1 = _group("Port_1", address=0x1000, registers=[_register("Reg", fields=[_field("X", 0, 4)])])
        g2 = _group("Port_2", address=0x2000, registers=[_register("Reg", fields=[_field("X", 0, 4)])])
        device = _device([g0, g1, g2])
        result = GroupsFilter().apply(device)
        assert len(result.groups) == 1
        merged = result.groups[0]
        assert merged.offset == STRIDE_0X1000
