from pathlib import Path
import yaml

import pytest

import dral


class TestDralMapping:
    @pytest.mark.parametrize("mapping", ["test.mapping.1.yaml", "test.mapping.2.yaml"])
    def test_fields_mapping(self, mapping: str, datadir: Path):
        mapping_file = datadir / "mapping" / "input" / mapping
        mapping_object = dral.DralMapping(mapping_file)
        mapping_result = mapping_object.get()
        with open(datadir / "mapping" / "expected" / mapping, "r", encoding="utf-8") as file:
            expected_output = yaml.load(file, Loader=yaml.FullLoader)
        assert mapping_result == expected_output
