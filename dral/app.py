from __future__ import annotations

from pathlib import Path
from typing import Any, Type, Optional

import click
from rich.console import Console
from rich.traceback import install as traceback

from .adapter.base import BaseAdapter
from .adapter.svd import SvdAdapter
from .adapter.white_black_list import WhiteBlackListAdapter
from .filter import BanksFilter, BlackListFilter, WhiteListFilter
from .format import CppFormat, PythonFormat
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
    type=click.Choice(["c", "cpp", "python"], case_sensitive=False),
    help="Specify the programming language for which you want to generate files.",
)
@click.option(
    "-t",
    "--template_type",
    default="mcu",
    show_default=True,
    type=click.Choice(["mcu", "serial"], case_sensitive=False),
    help="Specify the template type used to generate files.",
)
@click.option(
    "-T",
    "--template_path",
    type=click.Path(exists=True, resolve_path=True, path_type=Path),
    help="Specify path to template files used to generate files.",
)
@click.option(
    "-m",
    "--mapping",
    type=click.Path(exists=True, resolve_path=True, path_type=Path),
    help="Specify mapping file to overwrite values with constants.",
)
@click.option(
    "-s",
    "--skip_banks",
    is_flag=True,
    help="Skip automatic registers banks detection.",
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
def cli(input: Path, output: Path, language: str, template_type: str, template_path: Optional[Path], mapping: Path, skip_banks: bool, white_list: Optional[Path], black_list: Optional[Path]) -> None:  # noqa: C901
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
        white_list_adapter = WhiteBlackListAdapter(white_list)
        white_list_objects = white_list_adapter.convert()
    else:
        white_list_objects = None

    if black_list:
        black_list_adapter = WhiteBlackListAdapter(black_list)
        black_list_objects = black_list_adapter.convert()
    else:
        black_list_objects = None

    template_dir_list = [Utils.get_template_dir(language, template_type)]
    model_template_dir_list = [Utils.get_model_template_dir(language)]
    if template_path:
        template_dir_list.insert(0, template_path)
        template_dir_list.insert(0, template_path / language)
        model_template_dir_list.insert(0, template_path)
        model_template_dir_list.insert(0, template_path / "model" / language)
    forbidden_words = Utils.get_forbidden_words(language)

    info = "[bold green]Generating D-Ral files..."
    with console.status(info):
        # Convert data using adapter
        adapter = DRAL_CUSTOM_ADAPTER(input)
        device = adapter.convert()

        # Apply filters
        filters: Any = []
        if black_list_objects is not None:
            filters.append(BlackListFilter(black_list_objects))
        if white_list_objects is not None:
            filters.append(WhiteListFilter(white_list_objects))
        if not skip_banks:
            filters.append(BanksFilter())
        for item in filters:
            device = item.apply(device)

        # Generate D-RAL data
        generator = DralGenerator(forbidden_words, mapping)
        peripherals_object = generator.get_peripherals(device, template_dir_list)

        # Generate D-RAL register model file
        model_object = generator.get_model(model_template_dir_list)

        # Make output
        output = output / "dralOutput"

        chip = Utils.get_device_info(input)[0]
        output_format: Any = CppFormat(output, "dral", chip)
        if language == "cpp":
            output_format = CppFormat(output, "dral", chip)
        elif language == "python":
            output_format = PythonFormat(output, chip)
        output_format.make(peripherals_object, model=model_object)

    console.print(f"Successfully generated D-Ral files to {output}", style="green")


def main() -> None:
    cli()  # noqa: E1120


if __name__ == "__main__":
    main()
