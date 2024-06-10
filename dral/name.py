import re
from difflib import SequenceMatcher


class NameError(Exception):
    pass


def _get_name_difference(name_a: str, name_b: str) -> tuple[str, int, int]:
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
    return "none", 0, 0


def _get_group_marker(left: str, right: str) -> str:
    marker = "x"
    if left and left[-1] != "_":
        marker = "_" + marker
    if right and right[0] != "_":
        marker = marker + "_"
    return marker


def is_similar_name(name_a: str, name_b: str) -> bool:
    difference, _, _ = _get_name_difference(name_a, name_b)
    if difference in ["equal", "insert", "delete", "replace"]:
        return True
    return False


def get_common_name(namelist: list[str]) -> str:
    similar = 0
    for name in namelist:
        if is_similar_name(name, namelist[0]):
            similar += 1
    if similar != len(namelist):
        raise NameError("Could not get a common name - names are not similar")
    name = namelist[0]
    difference, i1, i2 = _get_name_difference(namelist[0], namelist[1])
    if difference in ["insert", "delete", "replace"]:
        marker = _get_group_marker(name[:i1], name[i2:])
        return name[:i1] + marker + name[i2:]
    raise NameError("Could not get a common name")


def upper_camel_case(string: str) -> str:
    return "".join(x.capitalize() for x in string.lower().split("_"))


def lower_camel_case(string: str) -> str:
    return string[0].lower() + upper_camel_case(string)[1:]
