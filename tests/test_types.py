import pytest
import yaml

import dral


class TestDralTypes:

    @pytest.fixture
    def test_fields(self, datadir):
        test_fields_file = datadir / "types" / "fields.yaml"
        with open(test_fields_file, "r") as test_fields:
            fields = yaml.load(test_fields, Loader=yaml.FullLoader)
        return fields

    @pytest.mark.parametrize("field", ["field1", "field2"])
    def test_field_type_creation(self, field, test_fields):
        test_field = test_fields[field]

        field = dral.Field(**test_field)

        assert field.name == test_field["name"]
        assert field.description == test_field["description"]
        assert field.position == test_field["position"]
        assert field.mask == test_field["mask"]
        assert field.width == test_field["width"]


    @pytest.mark.parametrize("field_a", ["field1", "field2", "field3", "field4"])
    @pytest.mark.parametrize("field_b", ["field1", "field2", "field3", "field4"])
    def test_field_type_comparison(self, field_a, field_b, test_fields):
        test_field_a = dral.Field(**test_fields[field_a])
        test_field_b = dral.Field(**test_fields[field_b])

        if field_a == field_b:
            assert test_field_a == test_field_b
        else:
            assert test_field_a != test_field_b
