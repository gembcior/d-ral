from __future__ import annotations

from collections.abc import Sequence

from natsort import natsorted

from dral.core.objects import (
    DralDevice,
    DralField,
    DralGroup,
    DralGroupInstance,
    DralObject,
    DralRegister,
)
from dral.filter.base import BaseFilter
from dral.utils.name import get_common_name, get_name_difference, is_similar_name


class GroupsFilter(BaseFilter):
    def _is_similar_name(self, object_a: DralObject, object_b: DralObject) -> bool:
        return is_similar_name(object_a.name, object_b.name)

    def _compare_fields(self, field_a: DralField, field_b: DralField) -> bool:
        if field_a.name != field_b.name:
            return False
        if field_a.position != field_b.position:
            return False
        if field_a.width != field_b.width:  # noqa: SIM103
            return False
        return True

    def _is_field_in_fields(self, field: DralField, fields: list[DralField]) -> bool:
        return any(self._compare_fields(field, item) for item in fields)

    def _has_the_same_fields(self, register_a: DralRegister, register_b: DralRegister) -> bool:
        diff = []
        for field in register_a.fields + register_b.fields:
            if not self._is_field_in_fields(field, register_a.fields) or not self._is_field_in_fields(field, register_b.fields):
                diff.append(field)
        return len(diff) == 0

    def _compare_registers(self, register_a: DralRegister, register_b: DralRegister) -> bool:
        if not self._has_the_same_fields(register_a, register_b):
            return False
        if not self._is_similar_name(register_a, register_b):  # noqa: SIM103
            return False
        return True

    def _is_register_in_registers(self, register: DralRegister, registers: list[DralRegister]) -> bool:
        return any(self._compare_registers(register, item) for item in registers)

    def _has_the_same_registers(self, group_a: DralGroup, group_b: DralGroup) -> bool:
        diff = []
        for register in group_a.registers + group_b.registers:
            if not self._is_register_in_registers(register, group_a.registers) or not self._is_register_in_registers(register, group_b.registers):
                diff.append(register)
        return len(diff) == 0

    def _is_group_in_groups(self, group: DralGroup, groups: list[DralGroup]) -> bool:
        return any(self._compare_groups(group, item) for item in groups)

    def _has_the_same_groups(self, group_a: DralGroup, group_b: DralGroup) -> bool:
        diff = []
        for group in group_a.groups + group_b.groups:
            if not self._is_group_in_groups(group, group_a.groups) or not self._is_group_in_groups(group, group_b.groups):
                diff.append(group)
        return len(diff) == 0

    def _compare_groups(self, group_a: DralGroup, group_b: DralGroup) -> bool:
        if not self._is_similar_name(group_a, group_b):
            return False
        if not self._has_the_same_registers(group_a, group_b):
            return False
        if not self._has_the_same_groups(group_a, group_b):  # noqa: SIM103
            return False
        return True

    def _get_group_offset(self, offsets: list[int]) -> list[int] | int:
        offsets_diff = [offsets[i + 1] - offsets[i] for i in range(len(offsets) - 1)]
        if len(set(offsets_diff)) == 1:
            return abs(offsets_diff[0])
        return list(map(lambda x: abs(x - offsets[0]), offsets))

    def _merge_groups(self, list_of_groups: list[list[DralGroup]]) -> list[DralGroup]:
        output = []
        for groups in list_of_groups:
            groups.sort(key=lambda x: x.address)
            instances = [DralGroupInstance(group.name, group.address) for group in groups]
            offset = self._get_group_offset([group.address for group in groups])
            new_name = get_common_name([group.name for group in groups])
            new = DralGroup(
                name=new_name,
                description=groups[0].description,
                address=groups[0].address,
                offset=offset,
                instances=instances,
                groups=groups[0].groups,
                registers=groups[0].registers,
            )
            output.append(new)
        return output

    def _get_merged_groups(self, groups: list[DralGroup]) -> list[DralGroup]:
        i = 0
        merged = []
        while i < len(groups):
            same = [group for group in reversed(groups) if self._compare_groups(groups[i], group)]
            if len(same) < 2 or not self._can_merge(same):
                i = i + 1
                continue
            for item in same:
                groups.remove(item)
            merged.append(same)
        return groups + self._merge_groups(merged)

    def _merge_registers(self, list_of_registers: list[list[DralRegister]]) -> list[DralGroup]:
        output = []
        for registers in list_of_registers:
            registers.sort(key=lambda x: x.address)
            instances = [DralGroupInstance(register.name, register.address) for register in registers]
            offset = self._get_group_offset([register.address for register in registers])
            new_name = get_common_name([register.name for register in registers])
            new = DralGroup(
                name=new_name,
                description=registers[0].description,
                address=registers[0].address,
                offset=offset,
                instances=instances,
                registers=[
                    DralRegister(
                        name=new_name,
                        description=registers[0].description,
                        access=registers[0].access,
                        value_type=registers[0].value_type,
                        address=0,
                        size=registers[0].size,
                        reset_value=registers[0].reset_value,
                        fields=registers[0].fields,
                    )
                ],
            )
            output.append(new)
        return output

    def _can_merge(self, same: Sequence[DralObject]) -> bool:
        same = natsorted(same, key=lambda x: x.name)
        backets = []
        for i_item in same:
            backet = [j_item for j_item in same if self._is_similar_name(i_item, j_item)]
            if backet not in backets and backet != same:
                backets.append(backet)
        return len(backets) < 2

    def _get_merged_registers(self, registers: list[DralRegister]) -> tuple[list[DralRegister], list[DralGroup]]:
        i = 0
        merged = []
        while i < len(registers):
            same = [register for register in reversed(registers) if self._compare_registers(registers[i], register)]
            if len(same) < 2 or not self._can_merge(same):
                i = i + 1
                continue
            for item in same:
                registers.remove(item)
            merged.append(same)
        return (registers, self._merge_registers(merged))

    def _merge_all_groups(self, groups: list[DralGroup]) -> list[DralGroup]:
        groups = self._get_merged_groups(groups)
        to_update = [groups]
        to_update_next: list[list[DralGroup]] = []
        while True:
            for next in to_update:
                to_update_next = []
                for i, group in enumerate(next):
                    next[i].groups = self._get_merged_groups(group.groups)
                    to_update_next.append(next[i].groups)
            to_update = to_update_next
            if not to_update:
                break
        return groups

    def _merge_all_registers(self, groups: list[DralGroup]) -> list[DralGroup]:
        for i, group in enumerate(groups):
            groups[i].registers, merged = self._get_merged_registers(group.registers)
            merged_groups = self._merge_all_registers(group.groups)
            groups[i].groups = merged + merged_groups
        return groups

    def _rename_group(self, group: DralGroup) -> str:
        instances = [instance.name for instance in group.instances]
        _, i1, i2 = get_name_difference(instances[0], instances[1])
        add = sorted([name[i1:i2] for name in instances])
        return f"{group.name[:i1]}_{'_'.join(add)}{group.name[i1:]}"

    def _resolve_duplicated_groups(self, groups: list[DralGroup]) -> list[DralGroup]:
        if not groups:
            return groups
        duplicated: dict[str, list[str]] = {}
        for group in groups:
            if group.name in duplicated:
                duplicated[group.name].append(group.name)
            else:
                duplicated[group.name] = [group.name]
        buckets = []
        for bucket in duplicated.values():
            if len(bucket) < 2:
                continue
            buckets.append(bucket)
        for bucket in buckets:
            for i, group in enumerate(groups):
                if group.name in bucket:
                    groups[i].name = self._rename_group(group)
        return groups

    def _rename_duplicated_groups(self, groups: list[DralGroup]) -> list[DralGroup]:
        groups = self._resolve_duplicated_groups(groups)
        for i, group in enumerate(groups):
            groups[i].groups = self._rename_duplicated_groups(group.groups)
        return groups

    def apply(self, device: DralDevice) -> DralDevice:
        device.groups = self._merge_all_groups(device.groups)
        device.groups = self._merge_all_registers(device.groups)
        device.groups = self._rename_duplicated_groups(device.groups)
        device.link_parent()
        return device
