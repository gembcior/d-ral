from __future__ import annotations

import importlib.resources as resources
from pathlib import Path
from typing import Optional

import pytest
import yaml

import dral


class TestDralGenerator:
    def get_svd_file(self, brand: str, chip: str) -> Optional[Path]:
        try:
            with resources.path(f"dral.devices.{brand}", f"{chip}.svd") as svd:
                return Path(svd)
        except ModuleNotFoundError:
            return None

    def get_template_dir(self, language: str) -> Optional[Path]:
        try:
            with resources.path(f"dral.templates.{language}", "__init__.py") as template_dir:
                return Path(template_dir).parent
        except ModuleNotFoundError:
            return None

    def get_forbidden_words(self, language: str) -> Optional[Path]:
        try:
            with resources.path(f"dral.templates.{language}", "__init__.py") as template_dir:
                return Path(template_dir).parent / "forbidden.yaml"
        except ModuleNotFoundError:
            return None

    def get_template(self, template_dir: Path, template: str) -> Optional[Path]:
        template_path = template_dir / template
        if not template_path.exists():
            return None
        return template_path

    @pytest.mark.parametrize("device", ["arm.example.example1", "stm32.f4.stm32f411", "stm32.f4.stm32f446"])
    @pytest.mark.parametrize("template", ["mcu", "serial"])
    @pytest.mark.parametrize("language", ["cpp", "python", "c"])
    def test_supported_svd_devices(self, device: str, template: str, language: str, datadir: Path):
        svd = device.split(".")
        svd_path = self.get_svd_file(f"{svd[0]}.{svd[1]}", svd[2])
        if svd_path is None:
            pytest.skip(f"Not supported devices: {device}")
        language_template_dir = self.get_template_dir(language)
        if language_template_dir is None:
            pytest.skip(f"Not supported language: {language}")
        template_dir = self.get_template(language_template_dir, template)
        if template_dir is None:
            pytest.skip(f"Not supported template: {template} for language: {language}")

        adapter = dral.adapter.SvdAdapter(svd_path)
        device_data = adapter.convert()
        device_data = dral.filter.BanksFilter().apply(device_data)
        # forbidden_words = self.get_forbidden_words(language)

        with open(datadir / "generator" / language / template / "mapping.yaml", "r", encoding="utf-8") as mapping_file:
            mapping = yaml.load(mapping_file, Loader=yaml.FullLoader)
        generator = dral.DralGenerator(template_dir)
        objects = generator.generate(device_data, mapping=mapping)

        with open(datadir / "generator" / language / template / f"{device}.yaml") as data:
            expected_output = []
            for item in yaml.load(data, Loader=yaml.FullLoader):
                expected_output.append(dral.DralOutputFile(item["name"], item["content"]))

        # with open(f"{device}-{template}-{language}.yaml", "w") as myfile:
        #     temp = []
        #     for item in objects:
        #         temp.append({"name": item.name, "content": item.content})
        #     yaml.dump(temp, myfile)

        result = objects == expected_output
        assert result
