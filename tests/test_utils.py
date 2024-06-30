from __future__ import annotations

from pathlib import Path

import pytest

from dral.utils import Utils

forbidden_words = {
    "cpp": [
        "and",
        "class",
        "goto",
        "int",
        "long",
        "new",
    ],
    "model": ["value"],
}


class TestDralUtils:
    @pytest.mark.parametrize("template", ["mcu"])
    @pytest.mark.parametrize("language", ["cpp", "python"])
    def test_get_template_dir(self, template: str, language: str, rootdir: Path):
        templates_subpath = "dral/templates"
        result = Utils.get_template_dir(language, template)
        expected = rootdir.parents[0] / templates_subpath / language / template
        assert expected == result

    @pytest.mark.parametrize("language", ["cpp"])
    def test_get_forbidden_words(self, language: str):
        words = Utils.get_forbidden_words(language)
        expected = forbidden_words[language] + forbidden_words["model"]
        assert all(word in words for word in expected)
