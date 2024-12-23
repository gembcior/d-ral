from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dral.adapter.base import BaseAdapter
from dral.adapter.svd import SvdAdapter
from dral.adapter.white_black_list import WhiteBlackListAdapter
from dral.core.generator import (
    DralGenerator,
    MultiOutputGenerator,
    SingleOutputGenerator,
)
from dral.core.objects import DralSuffix
from dral.filter import BlackListFilter, FilterSupervisor, GroupsFilter, WhiteListFilter
from dral.formatter.cpp import CppFormatter
from dral.formatter.html import HtmlFormatter
from dral.layout.cpp import CppLayout
from dral.layout.html import HtmlLayout
from dral.utils.utils import Utils

from .context import CppContext, DralContext, HtmlContext


@dataclass
class DralAppOptions:
    input_file: Path
    output_path: Path
    language: str
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
    filters = []
    if options.black_list:
        filters.append(get_black_list_filter(options.black_list))
    if options.white_list:
        filters.append(get_white_list_filter(options.white_list))
    if not options.skip_groups_detection:
        filters.append(get_groups_filter())
    return FilterSupervisor(filters)


def get_adapter() -> BaseAdapter:
    return SvdAdapter()


def get_multi_output_generator(options: DralAppOptions) -> DralGenerator:
    template_dir_list = get_template_dir_list(options)
    suffix = DralSuffix()
    forbidden_words = get_forbidden_words(options.language)
    return MultiOutputGenerator(template_dir_list, suffix, forbidden_words)


def get_single_output_generator(options: DralAppOptions) -> DralGenerator:
    template_dir_list = get_template_dir_list(options)
    suffix = DralSuffix()
    forbidden_words = get_forbidden_words(options.language)
    return SingleOutputGenerator(template_dir_list, suffix, forbidden_words)


def get_cpp_context(options: DralAppOptions) -> CppContext:
    adapter = get_adapter()
    generator = get_multi_output_generator(options)
    filter = get_filter_supervisor(options)
    formatter = CppFormatter()
    layout = CppLayout(options.output_path)
    return CppContext(adapter, generator, filter, formatter, layout, options.access_type)


def get_html_context(options: DralAppOptions) -> HtmlContext:
    adapter = get_adapter()
    generator = get_single_output_generator(options)
    filter = get_filter_supervisor(options)
    formatter = HtmlFormatter()
    layout = HtmlLayout(options.output_path)
    return HtmlContext(adapter, generator, filter, formatter, layout)


def get_context(options: DralAppOptions) -> DralContext:
    if options.language == "cpp":
        return get_cpp_context(options)
    elif options.language == "html":
        return get_html_context(options)
    raise ValueError(f"Unsupported language: {options.language}")
