import sys
from typing import Any, List, Tuple

from rich.console import Console

from ..types import Bank, Device, Register
from .base import BaseFilter


class BanksFilter(BaseFilter):
    # TODO refactor register banks support
    def _find_register_banks(self, registers: List[Register]) -> List[List[Register]]:  # noqa: C901
        def get_symmetric_difference(str1: str, str2: str) -> List[str]:
            from difflib import Differ

            differ = Differ()
            output = []
            for item in list(differ.compare(str1, str2)):
                if "+" in item:
                    output.append(item.replace("+", "").strip())
                elif "-" in item:
                    output.append(item.replace("-", "").strip())
            return output

        def is_list_of_digits(digits: List[Any]) -> bool:
            for item in digits:
                if not item.isdigit():
                    return False
            return True

        def only_one_pos(s1: str, s2: str) -> bool:
            ok = False
            if len(s1) != len(s2):
                return False
            for c1, c2 in zip(s1, s2):
                if c1 != c2:
                    if ok:
                        return False
                    else:
                        ok = True
            return ok

        def compare(item1: Register, item2: Register) -> bool:
            fields1 = item1.fields
            fields2 = item2.fields
            diff = [i for i in fields1 + fields2 if i not in fields1 or i not in fields2]
            if len(diff) == 0:
                if item1.name != item2.name:
                    symmetric_diff = get_symmetric_difference(item1.name, item2.name)
                    if is_list_of_digits(symmetric_diff):
                        return True
                    else:
                        # TODO
                        if only_one_pos(item1.name, item2.name):
                            return True
                        return False
                else:
                    return True
            return False

        banks = []
        registers_copy = registers.copy()
        for reg in registers:
            same = []
            for item in registers_copy:
                if compare(reg, item):
                    same.append(item)
            if len(same) > 1:
                banks.append(same)
                for item in same:
                    registers_copy.remove(item)
        return banks

    def _get_register_banks_offsets(self, registers: List[Register]) -> Tuple[Any, int]:
        offsets = []
        for item in registers:
            offsets.append(item.offset)
        diff = [offsets[i + 1] - offsets[i] for i in range(len(offsets) - 1)]  # type: ignore[operator]
        if len(set(diff)) != 1:
            console = Console()
            console.print(f"[red]ERROR: Register banks offset not consistent: {offsets}")
            console.print("Registers dump:")
            console.print(registers)
            sys.exit()
        min_offset = min(offsets)  # type: ignore[type-var]
        return min_offset, diff[0]

    def _get_register_bank_name(self, bank: List[Register]) -> str:
        from difflib import SequenceMatcher

        differ = SequenceMatcher(None, bank[0].name, bank[1].name)
        replace = differ.get_opcodes()[1]
        if replace[0] == "replace":
            position = replace[1]
            name = bank[0].name
            name = name[:position] + "x" + name[position + 1 :]
            return name
        elif replace[0] == "equal":
            name = bank[0].name
            if (len(name) - 1) == len(name[replace[1] : replace[2]]):
                if replace[1] > 0:
                    name = "x" + name[replace[1] : replace[2]]
                else:
                    name = name[replace[1] : replace[2]] + "x"
                return name
        console = Console()
        console.print(f"[red]ERROR: Wrong register bank name {bank[0].name}")
        sys.exit()

    def _merge_register_banks(self, registers: List[List[Register]]) -> List[Bank]:
        register_banks = []
        for bank in registers:
            first_offset, bank_offset = self._get_register_banks_offsets(bank)
            name = self._get_register_bank_name(bank)
            reg = Bank(
                name=name,
                description=bank[0].description,
                offset=first_offset,
                size=bank[0].size,
                access=bank[0].access,
                reset_value=bank[0].reset_value,
                bank_offset=bank_offset,
                fields=bank[0].fields,
            )
            register_banks.append(reg)
        return register_banks

    def _get_register_banks(self, registers: List[Register]) -> List[Bank]:
        register_banks = []
        banks = self._find_register_banks(registers)
        if banks:
            register_banks = self._merge_register_banks(banks)
        return register_banks

    def apply(self, device: Device) -> Device:
        for i, item in enumerate(device.peripherals):
            device.peripherals[i]._banks = self._get_register_banks(item.registers)  # noqa: W0212
        return device
