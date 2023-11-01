from __future__ import annotations

from pathlib import Path
from typing import Any, Type

import click
import yaml
from rich.console import Console
from rich.traceback import install as traceback

from .adapter.base import BaseAdapter
from .adapter.svd import SvdAdapter
from .adapter.white_black_list import WhiteBlackListAdapter
from .filter import BanksFilter, BlackListFilter, ExcludeFilter, WhiteListFilter
from .format import CppFormat, PythonFormat
from .generator import DralGenerator, DralOutputFile
from .template import DralTemplate
from .utils import Utils

DRAL_CUSTOM_ADAPTER = SvdAdapter


def override_adapter(adapter: Type[BaseAdapter]) -> None:
    global DRAL_CUSTOM_ADAPTER  # noqa: W0603
    DRAL_CUSTOM_ADAPTER = adapter  # type: ignore[assignment]


@click.command()  # type: ignore[arg-type] # noqa
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
def cli(input, output, language, template_type, template_path, mapping, skip_banks, white_list, black_list):  # type: ignore[no-untyped-def] # noqa: C901
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
        white_list = white_list_adapter.convert()
    else:
        white_list = None

    if black_list:
        black_list_adapter = WhiteBlackListAdapter(black_list)
        black_list = black_list_adapter.convert()
    else:
        black_list = None

    template_dir_list = [Utils.get_template_dir(language, template_type)]
    if template_path:
        template_dir_list.insert(0, template_path)
    template_object = DralTemplate(template_dir_list)

    if mapping:
        with open(mapping, "r", encoding="utf-8") as mapping_file:
            mapping = yaml.load(mapping_file, Loader=yaml.FullLoader)

    info = "[bold green]Generating D-Ral files..."
    with console.status(info):
        # Convert data using adapter
        adapter = DRAL_CUSTOM_ADAPTER(input)
        device = adapter.convert()

        # Apply filters
        filters: Any = []
        if black_list is not None:
            filters.append(BlackListFilter(black_list))
        if white_list is not None:
            filters.append(WhiteListFilter(white_list))
        if not skip_banks:
            filters.append(BanksFilter())
        for item in filters:
            device = item.apply(device)

        # Generate D-RAL data
        generator = DralGenerator(template_object)
        objects = generator.generate(device, mapping=mapping)

        # Get D-RAL register model file
        model_dir = Utils.get_model_dir(language)
        model_template = DralTemplate(model_dir)
        model_content = model_template.parse_from_template("model.dral", mapping={})
        dral_model_file = DralOutputFile("register_model", "".join(model_content))

        # Make output
        output = output / "dralOutput"

        chip = Utils.get_device_info(input)[0]
        output_format: Any = CppFormat(output, "dral", chip)
        if language == "cpp":
            output_format = CppFormat(output, "dral", chip)
        elif language == "python":
            output_format = PythonFormat(output, chip)
        output_format.make(objects, model=dral_model_file)

    console.print(f"Successfully generated D-Ral files to {output}", style="green")


def main() -> None:
    cli()  # type: ignore[misc] # noqa


if __name__ == "__main__":
    main()
