from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import dral


class TestDralTemplate:
    @pytest.fixture
    def test_data(self, datadir):
        return datadir / "template"

    def test_parse_from_string(self):
        input = "Test string [dral]object.item[#dral]. Rest, Dream, [dral]stuff.parameter[#dral], End."
        expected_output = ["Test string 0x1234. Rest, Dream, Protect, End."]
        mapping = {
            "object": {"item": "0x1234"},
            "stuff": {"parameter": "Protect"},
        }
        template_object = dral.DralTemplate()
        output = template_object.parse_from_string(input, mapping)
        assert output == expected_output

    @pytest.mark.parametrize("template", ["simple", "style", "include", "list", "mix", "numbers", "format"])
    def test_parse_from_template(self, template: str, test_data: Path):
        print("")
        template_dir = test_data / template
        template_object = dral.DralTemplate(template_dir)
        with open(template_dir / "mapping.yaml", "r", encoding="utf-8") as mapping_file:
            mapping = yaml.load(mapping_file, Loader=yaml.FullLoader)
        output = template_object.parse_from_template("root.dral", mapping)
        with open(template_dir / f"output.root.txt", "r", encoding="utf-8") as output_file:
            expected_output = output_file.readlines()
        assert output == expected_output
