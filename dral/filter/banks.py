from __future__ import annotations

from difflib import SequenceMatcher
from typing import List, Tuple

from ..types import Bank, Device, Field, Register
from .base import BaseFilter


class BankOffsetError(Exception):
    pass


class BankNameError(Exception):
    pass


class BanksFilter(BaseFilter):
    def _compare_fields(self, field_a: Field, field_b: Field) -> bool:
        if field_a.name != field_b.name:
            return False
        if field_a.position != field_b.position:
            return False
        if field_a.width != field_b.width:
            return False
        return True

    def _is_field_in_fields(self, field: Field, fields: List[Field]) -> bool:
        for item in fields:
            if self._compare_fields(field, item):
                return True
        return False

    def _has_the_same_fields(self, register_a: Register, register_b: Register) -> bool:
        diff = []
        for field in register_a.fields + register_b.fields:
            if not self._is_field_in_fields(field, register_a.fields) or not self._is_field_in_fields(field, register_b.fields):
                diff.append(field)
        return len(diff) == 0

    def _get_name_difference(self, register_a: Register, register_b: Register) -> Tuple[str, int, int]:
        if register_a.name == register_b.name:
            return "equal", 0, len(register_a.name)
        matcher = SequenceMatcher()
        matcher.set_seqs(register_a.name, register_b.name)
        opcodes = matcher.get_opcodes()
        replace_opcodes = [x for x in opcodes if x[0] == "replace"]
        delete_opcodes = [x for x in opcodes if x[0] == "delete"]
        insert_opcodes = [x for x in opcodes if x[0] == "insert"]
        opcodes_len = {"replace": len(replace_opcodes), "delete": len(delete_opcodes), "insert": len(insert_opcodes)}
        if opcodes_len["insert"] == 1 and opcodes_len["delete"] == 0 and opcodes_len["replace"] == 0:
            _, _, _, j1, j2 = insert_opcodes[0]
            insert_sequence = register_b.name[j1:j2]
            if insert_sequence.isdigit() or (j2 - j1) == 1:
                return "insert", j1, j2
        if opcodes_len["insert"] == 0 and opcodes_len["delete"] == 1 and opcodes_len["replace"] == 0:
            _, i1, i2, _, _ = delete_opcodes[0]
            delete_sequence = register_a.name[i1:i2]
            if delete_sequence.isdigit() or (i2 - i1) == 1:
                return "delete", i1, i2
        if opcodes_len["insert"] == 0 and opcodes_len["delete"] == 0 and opcodes_len["replace"] == 1:
            _, i1, i2, j1, j2 = replace_opcodes[0]
            replace_sequence = register_a.name[i1:i2] + register_b.name[j1:j2]
            if replace_sequence.isdigit() or ((i2 - i1) == 1 and (j2 - j1) == 1):
                return "replace", i1, i2
        return "none", 0, 0

    def _has_similar_name(self, register_a: Register, register_b: Register) -> bool:
        difference, _, _ = self._get_name_difference(register_a, register_b)
        if difference in ["equal", "insert", "delete", "replace"]:
            return True
        return False

    def _compare_registers(self, register_a: Register, register_b: Register) -> bool:
        if not self._has_the_same_fields(register_a, register_b):
            return False
        if not self._has_similar_name(register_a, register_b):
            return False
        return True

    def _find_register_banks(self, registers: List[Register]) -> List[List[Register]]:
        banks = []
        registers_copy = registers.copy()
        for reg in registers:
            same = []
            for i in reversed(range(len(registers_copy))):
                if self._compare_registers(reg, registers_copy[i]):
                    same.append(registers_copy[i])
                    del registers_copy[i]
            if len(same) > 1:
                banks.append(same)
        return banks

    def _get_register_banks_offsets(self, registers: List[Register]) -> Tuple[int, int]:
        registers.sort(key=lambda x: x.offset)
        offsets = []
        for i in range(len(registers) - 1):
            offsets.append(registers[i + 1].offset - registers[i].offset)
        if len(set(offsets)) == 1:
            return registers[0].offset, abs(offsets[0])
        raise BankOffsetError

    def _get_register_bank_name(self, bank: List[Register]) -> str:
        name = bank[0].name
        difference, i1, i2 = self._get_name_difference(bank[0], bank[1])
        if difference in ["insert", "delete", "replace"]:
            return name[:i1] + "x" + name[i2:]
        raise BankNameError

    def _merge_register_banks(self, registers: List[List[Register]]) -> List[Bank]:
        register_banks = []
        for bank in registers:
            try:
                first_offset, bank_offset = self._get_register_banks_offsets(bank)
                name = self._get_register_bank_name(bank)
            except (BankOffsetError, BankNameError):
                continue
            register_banks.append(
                Bank(
                    name=name,
                    description=bank[0].description,
                    offset=first_offset,
                    size=bank[0].size,
                    reset_value=bank[0].reset_value,
                    bank_offset=bank_offset,
                    fields=bank[0].fields,
                )
            )
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
