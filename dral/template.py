from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class DralMarkerError(Exception):
    pass


@dataclass
class DralMarkerAttribute:
    style: Optional[str] = None
    template: Optional[str] = None
    format: Optional[str] = None
    extras: Optional[str] = None


@dataclass
class DralMarkerItem:
    key: str
    parameter: str


@dataclass
class DralMarker:
    item: DralMarkerItem
    attributes: DralMarkerAttribute
    start: int
    end: int


@dataclass
class DralIncludeMarker:
    template: str
    start: int
    end: int


class DralTemplate:
    """
    A class to parse a template files

    ...

    Attributes
    ----------
    root : Path
        a Path object pointing to the root directory with template files

    Methods
    -------
    get(template, mapping)
        Get parsed string
    """

    def __init__(self, root: Optional[Path] = None):
        self._root = root

    def readlines(self, template: str) -> List[str]:
        """
        Get template file content

        Parameters
        ----------
        template : str
            Template file name

        Returns
        -------
        list[str]
        """
        if self._root is None:
            return []
        template_file = self._root / template
        if not template_file.exists():
            return []
        with open(template_file, "r", encoding="UTF-8") as file:
            template_content = file.readlines()
        return template_content

    def read(self, template: str) -> str:
        """
        Get template file content

        Parameters
        ----------
        template : str
            Template file name

        Returns
        -------
        str
        """
        if self._root is None:
            return ""
        template_file = self._root / template
        if not template_file.exists():
            return ""
        with open(template_file, "r", encoding="UTF-8") as file:
            template_content = file.read()
        return template_content

    def exists(self, template: str) -> bool:
        """
        Check if given template file exists

        Parameters
        ----------
        template : str
            Template file name

        Returns
        -------
        bool
        """
        if self._root is None:
            return False
        file = self._root / template
        return file.exists()

    def parse_from_template(self, template: str, mapping: Dict[str, Any]) -> List[str]:
        """
        Get parsed string from template file

        Parameters
        ----------
        template : str
            Template file name
        mapping : dict

        Returns
        -------
        str
        """
        input_content = self.readlines(template)
        output = self._parse_include(input_content)
        while output != input_content:
            input_content = output
            output = self._parse_include(input_content)
        output = self._parse_string(output, mapping)
        while output != input_content:
            input_content = output
            output = self._parse_string(output, mapping)
        return output

    def parse_from_string(self, text: Union[str, List[str]], mapping: Dict[str, Any]) -> List[str]:
        """
        Get parsed string from string

        Parameters
        ----------
        text : str
        mapping : dict

        Returns
        -------
        str
        """
        if isinstance(text, str):
            input_content = text.splitlines()
        else:
            input_content = text
        output = self._parse_include(input_content)
        while output != input_content:
            input_content = output
            output = self._parse_include(input_content)
        output = self._parse_string(output, mapping)
        while output != input_content:
            input_content = output
            output = self._parse_string(output, mapping)
        return output

    def _parse_attributes(self, attributes: str) -> DralMarkerAttribute:
        pattern = re.compile(r"(\w+?)=\"(.+?)\"")
        attributes_dict = {}
        for match in re.finditer(pattern, attributes):
            attributes_dict[match.group(1)] = match.group(2)
        return DralMarkerAttribute(**attributes_dict)

    def _parse_item(self, item: str) -> DralMarkerItem:
        key, parameter = item.split(".")
        return DralMarkerItem(key, parameter)

    def _get_markers(self, line: str) -> List[DralMarker]:
        pattern = re.compile(r"\[dral ?([^\[\]]*)\](.*?)\[#dral\]", flags=(re.MULTILINE | re.DOTALL))
        markers = []
        for match in re.finditer(pattern, line):
            attributes = self._parse_attributes(match.group(1))
            item = self._parse_item(match.group(2))
            markers.append(DralMarker(item, attributes, match.start(), match.end()))
        return markers

    def _get_list_replacement(self, substitution: List[Dict[str, Any]], marker: DralMarker, mapping: Dict[str, Any]) -> str:
        if marker.attributes.template is None:
            raise DralMarkerError
        new_substitution = []
        for item in substitution:
            item.update(mapping)
            new_substitution += self.parse_from_template(marker.attributes.template, item)
        leading_spaces = " " * marker.start
        new_substitution_string = (leading_spaces.join(new_substitution)).strip("\n")
        return new_substitution_string

    def _get_number_replacement(self, substitution: int, marker: DralMarker) -> str:
        if marker.attributes.format is not None:
            output = marker.attributes.format.format(substitution)
        else:
            output = str(substitution)
        output = output.replace("X", "x")
        return output

    def _get_system_replacement(self, marker: DralMarker) -> str:
        output = ""
        if marker.item.parameter == "year":
            output = str(datetime.now().year)
        return output

    def _get_replacement(self, marker: DralMarker, mapping: Dict[str, Any]) -> str:
        try:
            replacement = mapping[marker.item.key][marker.item.parameter]
        except KeyError as exception:
            if marker.item.key == "system":
                replacement = self._get_system_replacement(marker)
            else:
                raise DralMarkerError from exception
        if isinstance(replacement, list):
            output = self._get_list_replacement(replacement, marker, mapping)
        elif isinstance(replacement, int):
            output = self._get_number_replacement(replacement, marker)
        else:
            output = replacement
        if marker.attributes.style is not None:
            output = self._apply_style(output, marker.attributes.style)
        if marker.attributes.extras is not None:
            output = self._apply_extras(output, marker.attributes.extras)
        return output

    def _apply_style(self, line: str, style: str) -> str:
        if style == "uppercase":
            line = line.upper()
        elif style == "lowercase":
            line = line.lower()
        elif style == "capitalize":
            line = line.capitalize()
        elif style == "strip":
            line = line.strip(" \n\r")
        elif style == "LF":
            line = line + "\n"
        return line

    def _apply_extras(self, line: str, extras: str) -> str:
        raise NotImplementedError

    def _apply_replacement(self, line: str, substitution: str, marker: DralMarker) -> str:
        try:
            output = line[: marker.start] + substitution + line[marker.end :]
        except KeyError as exception:
            raise DralMarkerError from exception
        return output

    def _parse_line(self, line: str, mapping: Dict[str, Any]) -> str:
        dral_markers = self._get_markers(line)
        if not dral_markers:
            return line
        dral_markers.sort(reverse=True, key=lambda x: x.start)
        for marker in dral_markers:
            substitution = self._get_replacement(marker, mapping)
            line = self._apply_replacement(line, substitution, marker)
        return line

    def _parse_string(self, string: List[str], mapping: Dict[str, Any]) -> List[str]:
        content: List[str] = []
        for line in string:
            content += self._parse_line(line, mapping).splitlines(keepends=True)
        return content

    def _get_includes(self, line: str) -> List[DralIncludeMarker]:
        pattern = re.compile(r"\[dral\]include (.+)\[#dral\]", flags=(re.MULTILINE | re.DOTALL))
        markers = []
        for match in re.finditer(pattern, line):
            template = match.group(1)
            markers.append(DralIncludeMarker(template, match.start(), match.end()))
        return markers

    def _parse_include(self, string: List[str]) -> List[str]:
        content: List[str] = []
        for i in reversed(range(len(string))):
            dral_include_markers = self._get_includes(string[i])
            if not dral_include_markers:
                content.append(string[i])
                continue
            dral_include_markers.sort(reverse=True, key=lambda x: x.start)
            for marker in dral_include_markers:
                substitution = self.readlines(marker.template)
                substitution.reverse()
                content.append(substitution[0].rstrip("\n") + string[i][marker.end :])
                content += substitution[1:-1]
                content.append(string[i][: marker.start] + substitution[-1])
        content.reverse()
        return content
