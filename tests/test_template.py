from __future__ import annotations

from pathlib import Path

import pytest

import dral


class TestDralTemplate:
    def test_single_line_replace(self):
        input = ["Test string [dral]object.item[#dral]. Rest, Dream, [dral]stuff.parameter[#dral], End."]
        expected_output = ["Test string 0x1234. Rest, Dream, Protect, End."]
        mapping = {
            "object": {
                "default": {"item": "0x1234"},
            },
            "stuff": {
                "default": {"parameter": "Protect"},
            },
        }
        template_object = dral.DralTemplate("dral")
        output = template_object.replace(input, mapping)  # type: ignore[union-attr]
        assert output == expected_output

    @pytest.mark.parametrize("template", ["dral"])
    @pytest.mark.parametrize("object", ["field", "register", "bank", "peripheral"])
    @pytest.mark.parametrize("example", [1, 2])
    def test_replace_from_template(self, template: str, object: str, example: int, datadir: Path):
        template_object = dral.DralTemplate(template)
        mapping_object = dral.DralMapping(datadir / "template" / template / f"mapping.{example}.yaml")
        mapping = mapping_object.get()
        output = template_object.replace(f"{object}.dral", mapping)
        with open(datadir / "template" / template / f"{object}.{example}.txt", "r", encoding="utf-8") as file:
            expected_output = file.readlines()
        assert output == expected_output
