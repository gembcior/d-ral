from __future__ import annotations

from collections.abc import Sequence

from natsort import natsorted
from rich import inspect, print

from dral.filter.base import BaseFilter
from dral.name import _get_name_difference, get_common_name, is_similar_name
from dral.objects import (
    DralDevice,
    DralField,
    DralGroup,
    DralGroupInstance,
    DralObject,
    DralRegister,
)


class GroupsFilter(BaseFilter):
    def _is_similar_name(self, object_a: DralObject, object_b: DralObject) -> bool:
        return is_similar_name(object_a.name, object_b.name)

    def _compare_fields(self, field_a: DralField, field_b: DralField) -> bool:
        if field_a.name != field_b.name:
            return False
        if field_a.position != field_b.position:
            return False
        if field_a.width != field_b.width:
            return False
        return True

    def _is_field_in_fields(self, field: DralField, fields: list[DralField]) -> bool:
        for item in fields:
            if self._compare_fields(field, item):
                return True
        return False

    def _has_the_same_fields(self, register_a: DralRegister, register_b: DralRegister) -> bool:
        diff = []
        for field in register_a.fields + register_b.fields:
            if not self._is_field_in_fields(field, register_a.fields) or not self._is_field_in_fields(field, register_b.fields):
                diff.append(field)
        return len(diff) == 0

    def _compare_registers(self, register_a: DralRegister, register_b: DralRegister) -> bool:
        if not self._has_the_same_fields(register_a, register_b):
            return False
        if not self._is_similar_name(register_a, register_b):
            return False
        return True

    def _is_register_in_registers(self, register: DralRegister, registers: list[DralRegister]) -> bool:
        for item in registers:
            if self._compare_registers(register, item):
                return True
        return False

    def _has_the_same_registers(self, group_a: DralGroup, group_b: DralGroup) -> bool:
        diff = []
        for register in group_a.registers + group_b.registers:
            if not self._is_register_in_registers(register, group_a.registers) or not self._is_register_in_registers(register, group_b.registers):
                diff.append(register)
        return len(diff) == 0

    def _is_group_in_groups(self, group: DralGroup, groups: list[DralGroup]) -> bool:
        for item in groups:
            if self._compare_groups(group, item):
                return True
        return False

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
        if not self._has_the_same_groups(group_a, group_b):
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
            if len(same) < 2:
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
                        address=0,
                        size=registers[0].size,
                        default=registers[0].default,
                        fields=registers[0].fields,
                    )
                ],
            )
            output.append(new)
        return output

    # TODO: Draft. Try to think of a better way to implement this
    def remove_false_match(self, same: Sequence[DralObject]) -> Sequence[DralObject]:
        same = natsorted(same, key=lambda x: x.name)
        reference = []
        for i_item in same:
            if all([is_similar_name(j_item.name, i_item.name) for j_item in same]):
                reference.append(i_item)
        if len(reference) == len(same):
            return same
        if not reference or len(reference) > 1:
            raise ValueError("Could not find a reference item", [item.name for item in reference])
        reference = reference[0]
        backets = []
        for i_item in same:
            backet = [j_item for j_item in same if is_similar_name(i_item.name, j_item.name)]
            if backet not in backets and backet != same:
                backets.append(backet)
        if not backets or len(backets) == 1:
            return same
        print("Choose bucket")
        for i, backet in enumerate(backets):
            print(f"{i} - {[[(x.name, hex(x.address)) for x in backet]]}")
        choice = int(input("Enter the number of the bucket: "))
        return backets[choice]

    def _get_merged_registers(self, registers: list[DralRegister]) -> tuple[list[DralRegister], list[DralGroup]]:
        i = 0
        merged = []
        while i < len(registers):
            same = [register for register in reversed(registers) if self._compare_registers(registers[i], register)]
            same = self.remove_false_match(same)
            if len(same) < 2:
                i = i + 1
                continue
            for item in same:
                registers.remove(item)
            merged.append(same)
        return (registers, self._merge_registers(merged))

    def _merge_all_groups(self, groups: list[DralGroup]) -> list[DralGroup]:
        groups = self._get_merged_groups(groups)
        to_update = [groups]
        to_update_next = []
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

    # TODO: Implement this
    def _resolve_duplicated_groups(self, groups: list[DralGroup]) -> list[DralGroup]:
        duplicated = {}
        for group in groups:
            if group.name in duplicated:
                duplicated[group.name].append(group.name)
            else:
                duplicated[group.name] = [group.name]
        print(duplicated)
        return groups

    def apply(self, device: DralDevice) -> DralDevice:
        device.groups = self._merge_all_groups(device.groups)
        device.groups = self._merge_all_registers(device.groups)
        device.groups = self._resolve_duplicated_groups(device.groups)
        device.link_parent()
        return device
