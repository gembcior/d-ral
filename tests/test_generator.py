from __future__ import annotations

import json
from pathlib import Path

import pytest

from dral.adapter.svd import SvdAdapter
from dral.generator import DralGenerator
from dral.utils import Utils


class TestDralGenerator:
    @pytest.mark.parametrize("svd", ["arm_example"])
    @pytest.mark.parametrize("template", ["mcu"])
    @pytest.mark.parametrize("language", ["cpp"])
    def test_dral_generator(self, svd: str, template: str, language: str, datadir: Path):
        svd_path = datadir / "svd" / f"{svd}.svd"
        adapter = SvdAdapter()
        dral_device = adapter.convert(svd_path)
        forbidden_words = Utils.get_forbidden_words(language)
        template_dir_list = [Utils.get_template_dir(language, template)]

        generator = DralGenerator(template_dir_list, forbidden_words)
        dral_output_files = generator.generate("main.jinja", dral_device)

        # with open(datadir / "generator" / language  / f"{svd}.json", "w", encoding="utf-8") as data:
        #     data.write(json.dumps([x.asdict() for x in dral_output_files], indent=4))

        with open(datadir / "generator" / language / f"{svd}.json", "r", encoding="utf-8") as data:
            expected_dral_output_files = json.loads(data.read())

        assert [x.asdict() for x in dral_output_files] == expected_dral_output_files
