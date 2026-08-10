# =================================================================================
#
# MIT License
#
# Copyright (c) 2026 Gembcior
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# =================================================================================

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from dral.adapter import BaseAdapter
from dral.core.generator import DralGenerator, DralOutputFile, MultiOutputGenerator, SingleOutputGenerator
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
    def __init__(  # noqa: PLR0913
        self,
        adapter: BaseAdapter,
        generator: DralGenerator,
        filter: FilterSupervisor,
        formatter: DralFormatter,
        layout: DralLayout,
        access_type: str = "direct",
    ) -> None:
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


class HtmlContext(DralContext):
    def __init__(self, adapter: BaseAdapter, generator: DralGenerator, filter: FilterSupervisor, formatter: DralFormatter, layout: DralLayout) -> None:
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


class PythonContext(DralContext):
    def __init__(  # noqa: PLR0913
        self,
        adapter: BaseAdapter,
        multi_generator: MultiOutputGenerator,
        single_generator: SingleOutputGenerator,
        filter: FilterSupervisor,
        formatter: DralFormatter,
        layout: DralLayout,
    ) -> None:
        self._adapter = adapter
        self._multi_generator = multi_generator
        self._single_generator = single_generator
        self._filter = filter
        self._formatter = formatter
        self._layout = layout

    def parse(self, input_file: Path) -> DralDevice:
        device = self._adapter.convert(input_file)
        device = self._filter.apply(device)
        return device

    def generate(self, device: DralDevice) -> list[DralOutputFile]:
        files = self._multi_generator.generate("main.jinja", device)
        init_file = self._single_generator.generate("init.jinja", device, groups=[g.name for g in device.groups])
        files.append(DralOutputFile("__init__", init_file.content))
        return files

    def format(self, files: list[DralOutputFile]) -> list[DralOutputFile]:
        return self._formatter.format(files)

    def save(self, files: list[DralOutputFile], device: str) -> None:
        self._layout.make(files, device)
