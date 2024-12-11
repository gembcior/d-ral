from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Type

import click
from rich.console import Console
from rich.traceback import install as traceback

from dral.adapter.svd import SvdAdapter
from dral.adapter.white_black_list import WhiteBlackListAdapter
from dral.filter import BlackListFilter, GroupsFilter, WhiteListFilter
from dral.formatter import CppFormatter, DralFormatter
from dral.layout import CppLayout, DralLayout
from dral.objects import DralSuffix

from .adapter.base import BaseAdapter
from .generator import DralGenerator
from .utils import Utils

DRAL_CUSTOM_ADAPTER = SvdAdapter


def override_adapter(adapter: Type[BaseAdapter]) -> None:
    global DRAL_CUSTOM_ADAPTER  # noqa: W0603
    DRAL_CUSTOM_ADAPTER = adapter  # type: ignore[assignment]


@click.command()
@click.argument("input-file", type=click.Path(resolve_path=True, path_type=Path))
@click.option(
    "-O",
    "--output-path",
    type=click.Path(resolve_path=True, path_type=Path),
    default=Path("."),
    help="Output directory. Path where files will be generated. Default is current directory.",
)
@click.option(
    "-l",
    "--language",
    default="cpp",
    show_default=True,
    type=click.Choice(["cpp"], case_sensitive=False),
    help="Specify the programming language for which you want to generate files.",
)
@click.option(
    "-t",
    "--template-type",
    default="mcu",
    show_default=True,
    type=click.Choice(["mcu"], case_sensitive=False),
    help="Specify the template type used to generate files.",
)
@click.option(
    "-T",
    "--template-path",
    type=click.Path(exists=True, resolve_path=True, path_type=Path),
    help="Specify path to template files used to generate files.",
)
@click.option(
    "-s",
    "--skip-groups-detection",
    is_flag=True,
    help="Skip automatic registers groups detection.",
)
@click.option(
    "-f",
    "--skip-output-formatting",
    is_flag=True,
    help="Skip output formatting with auto format tools.",
)
@click.option(
    "-w",
    "--white-list",
    type=click.Path(exists=True, resolve_path=True, path_type=Path),
    help="Paripherals and Registers white list.",
)
@click.option(
    "-b",
    "--black-list",
    type=click.Path(exists=True, resolve_path=True, path_type=Path),
    help="Peripherals and Registers black list.",
)
@click.version_option()
def cli(  # noqa: C901
    input_file: Path,  # noqa: W0622
    output_path: Path,
    language: str,
    template_type: str,
    template_path: Optional[Path],
    skip_groups_detection: bool,
    skip_output_formatting: bool,
    white_list: Optional[Path],
    black_list: Optional[Path],
) -> None:
    """D-RAL - Device Register Access Layer

    Generate D-RAL files from INPUT-FILE.

    \b
    INPUT-FILE  - path to device description file.
    """
    traceback()
    console = Console()

    info = "[bold yellow]Preparing environment..."
    with console.status(info):
        if white_list:
            white_list_adapter = WhiteBlackListAdapter()
            white_list_objects = white_list_adapter.convert(white_list)
        else:
            white_list_objects = None

        if black_list:
            black_list_adapter = WhiteBlackListAdapter()
            black_list_objects = black_list_adapter.convert(black_list)
        else:
            black_list_objects = None

        template_dir_list = [Utils.get_template_dir(language, template_type)]
        if template_path:
            template_dir_list.insert(0, template_path)
            template_dir_list.insert(0, template_path / language)
        forbidden_words = Utils.get_forbidden_words(language)

    console.print(info)
    console.print(f"Environment ready", style="green")

    info = "[bold yellow]Generating D-RAL content..."
    with console.status(info):
        adapter = DRAL_CUSTOM_ADAPTER()
        # adapter = SvdAdapter()
        device = adapter.convert(input_file)

        filters: Any = []
        if black_list_objects is not None:
            filters.append(BlackListFilter(black_list_objects))
        if white_list_objects is not None:
            filters.append(WhiteListFilter(white_list_objects))
        if not skip_groups_detection:
            filters.append(GroupsFilter())
        for item in filters:
            device = item.apply(device)

        generator = DralGenerator(template_dir_list, DralSuffix(), forbidden_words)
        dral_output_files = generator.generate("main.jinja", device)
    console.print(info)
    console.print(f"Successfully generated D-RAL content", style="green")

    if not skip_output_formatting:
        info = "[bold yellow]Formatting D-RAL content..."
        with console.status(info):
            formatter: DralFormatter = CppFormatter()
            dral_output_files = formatter.format(dral_output_files)
        console.print(info)
        console.print(f"Successfully formatted D-RAL output files", style="green")

    info = "[bold yellow]Saving D-RAL content to files..."
    with console.status(info):
        output = output_path / "dralOutput"

        chip = device.name.lower()
        if language == "cpp":
            output_format: DralLayout = CppLayout(output, "dral", chip)
        else:
            raise ValueError(f"Language {language} not supported")

        output_format.make(dral_output_files)

    info = "[bold yellow]Downloading D-RAL model files..."
    with console.status(info):
        model_path = output / "cpp" / "model"
        Path.mkdir(model_path, parents=True, exist_ok=True)
        Utils.get_model_release(model_path)

    console.print(info)
    console.print(f"Successfully saved D-RAL files to {output}", style="green")


if __name__ == "__main__":
    cli()  # noqa: E1120
