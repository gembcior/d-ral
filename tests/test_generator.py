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

    def get_model_dir(self, language: str) -> Optional[Path]:
        try:
            with resources.path(f"dral.templates.model.{language}", "__init__.py") as model_dir:
                return Path(model_dir).parent
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
        forbidden_words = self.get_forbidden_words(language)
        mapping = datadir / "generator" / language / template / "mapping.yaml"
        generator = dral.DralGenerator(forbidden_words, mapping)
        peripherals_object = generator.get_peripherals(device_data, template_dir)

        with open(datadir / "generator" / language / template / f"{device}.yaml") as data:
            expected_output = []
            for item in yaml.load(data, Loader=yaml.FullLoader):
                expected_output.append(dral.DralOutputFile(item["name"], item["content"]))

        # with open(f"{device}-{template}-{language}.yaml", "w") as myfile:
        #     temp = []
        #     for item in peripherals_object:
        #         temp.append({"name": item.name, "content": item.content})
        #     yaml.dump(temp, myfile)

        result = peripherals_object == expected_output
        assert result

    @pytest.mark.parametrize("language", ["cpp", "python", "c"])
    def test_model_generation(self, language: str, datadir: Path):
        language_model_dir = self.get_model_dir(language)
        if language_model_dir is None:
            pytest.skip(f"Not supported language: {language}")
        forbidden_words = self.get_forbidden_words(language)
        mapping = datadir / "generator" / language / "model" / "mapping.yaml"
        generator = dral.DralGenerator(forbidden_words, mapping)
        model_object = generator.get_model(language_model_dir)

        with open(datadir / "generator" / language / "model" / f"register_model.yaml") as data:
            item = yaml.load(data, Loader=yaml.FullLoader)[0]
            expected_output = dral.DralOutputFile(item["name"], item["content"])

        # with open(f"register_model-{language}.yaml", "w") as myfile:
        #     temp = []
        #     temp.append({"name": model_object.name, "content": model_object.content})
        #     yaml.dump(temp, myfile)

        assert model_object == expected_output
