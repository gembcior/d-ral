from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Type

import click
from rich import inspect, print
from rich.console import Console
from rich.traceback import install as traceback

from dral.adapter.svd import SvdAdapter
from dral.adapter.white_black_list import WhiteBlackListAdapter
from dral.filter import BlackListFilter, GroupsFilter, WhiteListFilter
from dral.format import AsmFormat, CppFormat, PythonFormat
from dral.format.base import BaseFormat

from .adapter.base import BaseAdapter
from .generator import DralGenerator
from .utils import Utils

DRAL_CUSTOM_ADAPTER = SvdAdapter


def override_adapter(adapter: Type[BaseAdapter]) -> None:
    global DRAL_CUSTOM_ADAPTER  # noqa: W0603
    DRAL_CUSTOM_ADAPTER = adapter  # type: ignore[assignment]


@click.command()
@click.argument("input", type=click.Path(resolve_path=True, path_type=Path))
@click.argument("output", type=click.Path(resolve_path=True, path_type=Path))
@click.option(
    "-l",
    "--language",
    default="cpp",
    show_default=True,
    type=click.Choice(["c", "cpp", "python", "asm"], case_sensitive=False),
    help="Specify the programming language for which you want to generate files.",
)
@click.option(
    "-t",
    "--template-type",
    default="mcu",
    show_default=True,
    type=click.Choice(["mcu", "serial"], case_sensitive=False),
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
    input: Path,  # noqa: W0622
    output: Path,
    language: str,
    template_type: str,
    template_path: Optional[Path],
    skip_groups_detection: bool,
    white_list: Optional[Path],
    black_list: Optional[Path],
) -> None:
    """D-RAL - Device Register Access Layer

    Generate D-RAL files in the OUTPUT from INPUT.

    \b
    INPUT  - path to external device description file.

    \b
    OUTPUT - path where files will be generated.
    """
    traceback()
    console = Console()

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

    info = "[bold green]Generating D-Ral files..."
    # with console.status(info):
    # Convert data using adapter
    # adapter = DRAL_CUSTOM_ADAPTER(input)
    adapter = SvdAdapter()
    device = adapter.convert(input)

    # Apply filters
    filters: Any = []
    if black_list_objects is not None:
        filters.append(BlackListFilter(black_list_objects))
    if white_list_objects is not None:
        filters.append(WhiteListFilter(white_list_objects))
    if not skip_groups_detection:
        filters.append(GroupsFilter())
    for item in filters:
        device = item.apply(device)

        # Generate D-RAL data
    generator = DralGenerator(template_dir_list, forbidden_words)
    dral_output_files = generator.generate("main.jinja", device)
    # print(dral_output_files)
    #
    #     # Generate D-RAL register model file
    #     if language in ["asm"]:
    #         model_object = None
    #     else:
    #         model_object = generator.get_model(model_template_dir_list)
    #
    #     # Make output
    output = output / "dralOutput"
    #
    chip = Utils.get_device_info(input)[0]
    if language == "cpp":
        output_format: BaseFormat = CppFormat(output, "dral", chip)
    #     elif language == "python":
    #         output_format = PythonFormat(output, chip)
    #
    #     elif language == "asm":
    #         output_format = AsmFormat(output, chip)
    #     else:
    #         raise ValueError(f"Language {language} not supported")
    output_format.make(dral_output_files)
    #
    # console.print(f"Successfully generated D-Ral files to {output}", style="green")


def main() -> None:
    cli()  # noqa: E1120


if __name__ == "__main__":
    main()
