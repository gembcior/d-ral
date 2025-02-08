from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from dral.adapter import BaseAdapter
from dral.core.generator import DralGenerator, DralOutputFile
from dral.core.objects import DralDevice
from dral.filter import FilterSupervisor
from dral.formatter.base import DralFormatter
from dral.layout.base import DralLayout


class DralContext(ABC):
    @abstractmethod
    def parse(self, input_file: Path) -> DralDevice:
        pass

    @abstractmethod
    def generate(self, device: DralDevice) -> list[DralOutputFile] | DralOutputFile:
        pass

    @abstractmethod
    def format(self, files: list[DralOutputFile]) -> list[DralOutputFile]:
        pass

    @abstractmethod
    def save(self, files: list[DralOutputFile], device: str) -> None:
        pass


class CppContext(DralContext):
    def __init__(
        self,
        adapter: BaseAdapter,
        generator: DralGenerator,
        filter: FilterSupervisor,
        formatter: DralFormatter,
        layout: DralLayout,
        access_type: str = "direct",
    ):
        self._adapter = adapter
        self._generator = generator
        self._filter = filter
        self._formatter = formatter
        self._layout = layout
        self._access_type = access_type

    def parse(self, input_file: Path) -> DralDevice:
        device = self._adapter.convert(input_file)
        device = self._filter.apply(device)
        return device

    def generate(self, device: DralDevice) -> list[DralOutputFile] | DralOutputFile:
        return self._generator.generate(f"{self._access_type}.jinja", device)

    def format(self, files: list[DralOutputFile]) -> list[DralOutputFile]:
        return self._formatter.format(files)

    def save(self, files: list[DralOutputFile], device: str) -> None:
        self._layout.make(files, device)

    # def model(self):
    #     model_path = output / "cpp" / "model"
    #     Path.mkdir(model_path, parents=True, exist_ok=True)
    #     Utils.get_model_release(model_path)


class HtmlContext(DralContext):
    def __init__(self, adapter: BaseAdapter, generator: DralGenerator, filter: FilterSupervisor, formatter: DralFormatter, layout: DralLayout):
        self._adapter = adapter
        self._generator = generator
        self._filter = filter
        self._formatter = formatter
        self._layout = layout

    def parse(self, input_file: Path) -> DralDevice:
        device = self._adapter.convert(input_file)
        device = self._filter.apply(device)
        return device

    def generate(self, device: DralDevice) -> list[DralOutputFile] | DralOutputFile:
        return self._generator.generate("index.html", device)

    def format(self, files: list[DralOutputFile]) -> list[DralOutputFile]:
        return self._formatter.format(files)

    def save(self, files: list[DralOutputFile], device: str) -> None:
        self._layout.make(files, device)
