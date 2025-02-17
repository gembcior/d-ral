import re
from collections.abc import Sequence
from difflib import SequenceMatcher

from natsort import natsorted


class DralNameError(Exception):
    pass


class DralName:
    def __init__(self, namelist: Sequence[str], validate: bool = True):
        self._namelist = natsorted(namelist)
        if validate:
            self._validate()
        self._name = self._namelist[0]
        self._idx = self._calculate()

    def _validate(self):
        similar = 0
        for name in self._namelist:
            if self.is_similar_name(name, self._namelist[0]):
                similar += 1
        if similar != len(self._namelist):
            raise DralNameError("Could not get a common name. Names are not similar.", self._namelist)

    def _calculate(self) -> tuple[int, int]:
        difference, i1, i2 = self._get_name_difference(self._namelist[0], self._namelist[1])
        if difference in ["insert", "delete", "replace"]:
            return self._expand_digits(self._name, i1, i2)
        raise DralNameError("Could not get a common name. The way names are different not supported.", self._namelist)

    @classmethod
    def _get_name_difference(cls, name_a: str, name_b: str) -> tuple[str, int, int]:
        if name_a == name_b:
            return "equal", 0, len(name_a)
        matcher = SequenceMatcher()
        matcher.set_seqs(name_a, name_b)
        opcodes = matcher.get_opcodes()
        replace_opcodes = [x for x in opcodes if x[0] == "replace"]
        delete_opcodes = [x for x in opcodes if x[0] == "delete"]
        insert_opcodes = [x for x in opcodes if x[0] == "insert"]
        opcodes_len = {"replace": len(replace_opcodes), "delete": len(delete_opcodes), "insert": len(insert_opcodes)}
        pattern = re.compile(r"^[0-9]*_[0-9]+$")
        if opcodes_len["insert"] == 1 and opcodes_len["delete"] == 0 and opcodes_len["replace"] == 0:
            _, _, _, j1, j2 = insert_opcodes[0]
            insert_sequence = name_b[j1:j2]
            if insert_sequence.isdigit() or (j2 - j1) == 1 or re.match(pattern, insert_sequence):
                return "insert", j1, j2
        if opcodes_len["insert"] == 0 and opcodes_len["delete"] == 1 and opcodes_len["replace"] == 0:
            _, i1, i2, _, _ = delete_opcodes[0]
            delete_sequence = name_a[i1:i2]
            if delete_sequence.isdigit() or (i2 - i1) == 1 or re.match(pattern, delete_sequence):
                return "delete", i1, i2
        if opcodes_len["insert"] == 0 and opcodes_len["delete"] == 0 and opcodes_len["replace"] == 1:
            _, i1, i2, j1, j2 = replace_opcodes[0]
            replace_sequence = name_a[i1:i2] + name_b[j1:j2]
            if replace_sequence.isdigit() or ((i2 - i1) == 1 and (j2 - j1) == 1) or re.match(pattern, replace_sequence):
                return "replace", i1, i2
        if opcodes_len["insert"] == 1 and opcodes_len["delete"] == 1 and opcodes_len["replace"] == 0:
            _, i1, i2, _, _ = delete_opcodes[0]
            _, _, _, j1, j2 = insert_opcodes[0]
            replace_sequence = name_a[i1:i2] + name_b[j1:j2]
            if replace_sequence.isdigit():
                return "replace", i1 if i1 < j1 else j1, j2 if j2 > i2 else i2
        return "none", 0, 0

    def _get_name_marker(self, left: str, right: str, marker="x") -> str:
        if left and left[-1] != "_":
            marker = "_" + marker
        if right and right[0] != "_":
            marker = marker + "_"
        return marker

    def _expand_digits(self, name: str, i1: int, i2: int) -> tuple[int, int]:
        while i1 > 0 and name[i1 - 1].isdigit():
            i1 -= 1
        while i2 < len(name) and name[i2].isdigit():
            i2 += 1
        return i1, i2

    @classmethod
    def is_similar_name(cls, name_a: str, name_b: str) -> bool:
        difference, _, _ = cls._get_name_difference(name_a, name_b)
        return difference in ["equal", "insert", "delete", "replace"]

    def get_common_name(self) -> str:
        i1, i2 = self._idx
        marker = self._get_name_marker(self._name[:i1], self._name[i2:])
        return self._name[:i1] + marker + self._name[i2:]

    def get_instance_name(self, instance: str) -> str:
        i1, i2 = self._idx
        marker = self._get_name_marker(instance[:i1], instance[i2:], instance[i1:i2])
        return instance[:i1] + marker + instance[i2:]

    def get_difference_index(self) -> tuple[int, int]:
        return self._idx

    def get_difference_names(self) -> list[str]:
        i1, i2 = self._idx
        return natsorted([name[i1:i2] for name in self._namelist])


def upper_camel_case(string: str) -> str:
    return "".join(x.capitalize() for x in string.lower().split("_"))


def lower_camel_case(string: str) -> str:
    return string[0].lower() + upper_camel_case(string)[1:]
