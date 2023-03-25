from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterator, List, Optional, Union

from .mapping import MappingType
from .utils import Utils


class DralTemplate:
    def __init__(self, template: Union[str, Path]):
        if isinstance(template, Path):
            self._template = template
        else:
            self._template = Utils.get_template_dir(template)
        self._dral_prefix = r"\[dral\]"
        self._dral_sufix = r"\[#dral\]"
        self._dral_pattern = re.compile(
            self._dral_prefix + "(.*?)" + self._dral_sufix,
            flags=(re.MULTILINE | re.DOTALL),
        )

    def readlines(self, template: str) -> List[str]:
        template_file = self._template / template
        if not template_file.exists():
            return []
        with open(template_file, "r", encoding="UTF-8") as file:
            template_content = file.readlines()
        return template_content

    def read(self, template: str) -> str:
        template_file = self._template / template
        if not template_file.exists():
            return ""
        with open(template_file, "r", encoding="UTF-8") as file:
            template_content = file.read()
        return template_content

    def exists(self, template: str) -> bool:
        file = self._template / template
        return file.exists()

    def _apply_modifier(self, item: Union[str, List[str]], modifier: str) -> Union[str, List[str]]:
        output = item
        if isinstance(item, str):
            output = self._apply_string_modifier(item, modifier)
        elif isinstance(item, list):
            output = self._apply_list_modifier(item, modifier)
        return output

    def _apply_string_modifier(self, string: str, modifier: str) -> str:
        if modifier == "uppercase":
            string = string.upper()
        elif modifier == "lowercase":
            string = string.lower()
        elif modifier == "capitalize":
            string = string.capitalize()
        elif modifier == "strip":
            string = string.strip(" \n\r")
        elif modifier == "LF":
            string = string + "\n"
        return string

    def _apply_list_modifier(self, _list: List[str], modifier: str) -> List[str]:
        if modifier == "LF":
            _list = _list + ["\n"]
        return _list

    def _get_substitution(self, pattern: List[str], mapping: MappingType) -> Optional[str | list[str]]:
        object = pattern[0]
        if object not in mapping:
            return
        variant = pattern[2] if len(pattern) > 2 else "default"
        attr = pattern[1]
        try:
            output = mapping[object][variant][attr]
        except KeyError:
            return
        return output

    def _get_pattern_substitution(self, pattern: str, mapping: MappingType) -> Union[None, str, List[str]]:
        split_pattern = pattern.split("%")
        base = split_pattern[0].split(".")
        modifier = split_pattern[1:]
        substitution = self._get_substitution(base, mapping)
        if substitution is not None:
            for item in modifier:
                substitution = self._apply_modifier(substitution, item)
            return substitution
        return None

    def _find_all_dral_pattern(self, string: str) -> Iterator[Any]:
        return re.finditer(self._dral_pattern, string)

    def _replace_line(self, line: str, mapping: MappingType) -> Union[str, None]:
        dral_matches = self._find_all_dral_pattern(line)
        if dral_matches:  # type: ignore[truthy-bool]
            for match in dral_matches:
                pattern = match.group(1)
                position = match.start()
                leading_spaces = " " * position
                substitution = self._get_pattern_substitution(pattern, mapping)
                if substitution is not None:
                    pattern = f"{self._dral_prefix}{pattern}{self._dral_sufix}"
                    if isinstance(substitution, list):
                        substitution = (leading_spaces.join(substitution)).strip("\n")
                    line = re.sub(pattern, substitution, line, flags=(re.MULTILINE | re.DOTALL))  # type: ignore[arg-type]
            return line
        return None

    def _parse_string(self, string: List[str], mapping: MappingType) -> List[str]:
        content: List[str] = []
        for line in string:
            new_line = self._replace_line(line, mapping)
            if new_line is not None:
                content.append(new_line)
            else:
                content.append(line)
        new_content: List[str] = []
        for item in content:
            new_content = new_content + item.splitlines(True)
        return new_content

    def _continue(self, string: List[str], mapping) -> bool:
        for line in string:
            dral_matches = self._find_all_dral_pattern(line)
            if dral_matches:
                for match in dral_matches:
                    object = match.group(1)[0].split(".")[0]
                    if object in mapping:
                        return True
        return False

    def replace(self, template: str | List[str], mapping: MappingType) -> List[str]:
        if isinstance(template, str):
            template_content = self.readlines(template)
        else:
            template_content = template
        content = self._parse_string(template_content, mapping)
        content = self._parse_string(content, mapping)
        return content
