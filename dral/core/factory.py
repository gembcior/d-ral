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

from dataclasses import dataclass
from pathlib import Path

from dral.adapter.base import BaseAdapter
from dral.adapter.dral import DralAdapter
from dral.adapter.svd import SvdAdapter
from dral.adapter.white_black_list import WhiteBlackListAdapter
from dral.core.generator import (
    DralGenerator,
    MultiOutputGenerator,
    SingleOutputGenerator,
)
from dral.core.objects import DralSuffix
from dral.filter import BlackListFilter, FilterSupervisor, GroupsFilter, WhiteListFilter
from dral.filter.base import BaseFilter
from dral.filter.flat import FlatFilter
from dral.formatter.cpp import CppFormatter
from dral.formatter.html import HtmlFormatter
from dral.formatter.python import PythonFormatter
from dral.layout.asm import AssemblyLayout
from dral.layout.cpp import CppLayout
from dral.layout.html import HtmlLayout
from dral.layout.python import PythonLayout
from dral.layout.txt import TextLayout
from dral.utils.utils import Utils

from .context import AssemblyContext, CppContext, DralContext, HtmlContext, PythonContext, TextContext

DRAL_ADAPTER: type[BaseAdapter] = SvdAdapter


def override_adapter(adapter: type[BaseAdapter]) -> None:
    global DRAL_ADAPTER  # noqa: PLW0603
    DRAL_ADAPTER = adapter


@dataclass
class DralAppOptions:
    input_file: Path
    output_path: Path
    language: str
    adapter: str
    access_type: str
    template_path: Path | None
    skip_groups_detection: bool
    skip_output_formatting: bool
    white_list: Path | None
    black_list: Path | None


def get_template_dir_list(options: DralAppOptions) -> list[Path]:
    template_dir_list = [Utils.get_template_dir(options.language)]
    if options.template_path:
        template_dir_list.insert(0, options.template_path)
        template_dir_list.insert(0, options.template_path / options.language)
    return template_dir_list


def get_forbidden_words(language: str) -> list[str]:
    return Utils.get_forbidden_words(language)


def get_black_list_filter(black_list: Path) -> BlackListFilter:
    adapter = WhiteBlackListAdapter()
    objects = adapter.convert(black_list)
    return BlackListFilter(objects)


def get_white_list_filter(white_list: Path) -> WhiteListFilter:
    adapter = WhiteBlackListAdapter()
    objects = adapter.convert(white_list)
    return WhiteListFilter(objects)


def get_groups_filter() -> GroupsFilter:
    return GroupsFilter()


def get_filter_supervisor(options: DralAppOptions) -> FilterSupervisor:
    filters: list[BaseFilter] = []
    if options.black_list:
        filters.append(get_black_list_filter(options.black_list))
    if options.white_list:
        filters.append(get_white_list_filter(options.white_list))
    if not options.skip_groups_detection:
        filters.append(get_groups_filter())
    if options.adapter in ("dral", "svd") and options.language in ("asm", "txt"):
        filters.append(FlatFilter())
    return FilterSupervisor(filters)


def get_dral_adapter() -> DralAdapter:
    return DralAdapter()


def get_svd_adapter() -> SvdAdapter:
    return SvdAdapter()


def get_input_adapter(
    options: DralAppOptions,
) -> SvdAdapter | BaseAdapter:
    if options.adapter == "dral":
        return get_dral_adapter()
    if options.adapter == "svd":
        return get_svd_adapter()
    return DRAL_ADAPTER()


def get_multi_output_generator(options: DralAppOptions) -> DralGenerator:
    template_dir_list = get_template_dir_list(options)
    suffix = DralSuffix
    forbidden_words = get_forbidden_words(options.language)
    return MultiOutputGenerator(template_dir_list, suffix, forbidden_words)


def get_single_output_generator(options: DralAppOptions) -> DralGenerator:
    template_dir_list = get_template_dir_list(options)
    suffix = DralSuffix
    forbidden_words = get_forbidden_words(options.language)
    return SingleOutputGenerator(template_dir_list, suffix, forbidden_words)


def get_cpp_context(options: DralAppOptions) -> CppContext:
    adapter = get_input_adapter(options)
    generator = get_multi_output_generator(options)
    filter = get_filter_supervisor(options)
    formatter = CppFormatter()
    layout = CppLayout(options.output_path)
    return CppContext(adapter, generator, filter, formatter, layout, options.access_type)


def get_html_context(options: DralAppOptions) -> HtmlContext:
    adapter = get_input_adapter(options)
    generator = get_single_output_generator(options)
    filter = get_filter_supervisor(options)
    formatter = HtmlFormatter()
    layout = HtmlLayout(options.output_path)
    return HtmlContext(adapter, generator, filter, formatter, layout)


def get_python_context(options: DralAppOptions) -> PythonContext:
    adapter = get_input_adapter(options)
    multi_generator = get_multi_output_generator(options)
    single_generator = get_single_output_generator(options)
    filter = get_filter_supervisor(options)
    formatter = PythonFormatter()
    layout = PythonLayout(options.output_path)
    return PythonContext(adapter, multi_generator, single_generator, filter, formatter, layout)


def get_assembly_context(options: DralAppOptions) -> DralContext:
    adapter = get_input_adapter(options)
    generator = get_single_output_generator(options)
    filter = get_filter_supervisor(options)
    layout = AssemblyLayout(options.output_path)
    return AssemblyContext(adapter, generator, filter, layout)


def get_text_context(options: DralAppOptions) -> DralContext:
    adapter = get_input_adapter(options)
    generator = get_single_output_generator(options)
    filter = get_filter_supervisor(options)
    layout = TextLayout(options.output_path)
    return TextContext(adapter, generator, filter, layout)


def get_context(options: DralAppOptions) -> DralContext:
    if options.language == "cpp":
        return get_cpp_context(options)
    elif options.language == "html":
        return get_html_context(options)
    elif options.language == "python":
        return get_python_context(options)
    elif options.language == "asm":
        return get_assembly_context(options)
    elif options.language == "txt":
        return get_text_context(options)
    raise ValueError(f"Unsupported language: {options.language}")
