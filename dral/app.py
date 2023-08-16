from __future__ import annotations

import glob
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.traceback import install as traceback

from .adapter.svd import SvdAdapter
from .adapter.white_black_list import WhiteBlackListAdapter
from .filter import BanksFilter, BlackListFilter, ExcludeFilter, WhiteListFilter
from .format import CppFormat, PythonFormat
from .generator import DralGenerator, DralOutputFile
from .template import DralTemplate
from .utils import Utils


def print_supported_devices(ctx: Any, param: Any, value: Any) -> None:
    del param
    if not value or ctx.resilient_parsing:
        return
    devices_path = Path(__file__).parent / "devices"
    svd = glob.glob(f"{devices_path}/**/*.svd", recursive=True)
    svd.sort()
    for device in svd:
        chip, family, brand = Utils.get_device_info(Path(device))
        click.echo(f"{brand}::{family}::{chip}")
    ctx.exit()


def validate_svd(ctx: Any, param: Any, value: Any) -> Any:
    del ctx, param
    if Path(value).exists():
        return Path(value).resolve()
    value = Utils.get_svd_file(value)
    if value is not None:
        return value
    raise click.BadParameter("SVD must be a path to external SVD file or name of the already supported device")


@click.command()  # type: ignore[arg-type] # noqa
@click.argument("svd", type=click.UNPROCESSED, callback=validate_svd)
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
    "--template",
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
    "-e",
    "--exclude",
    multiple=True,
    type=click.Choice(["peripherals", "registers", "banks", "fields"], case_sensitive=False),
    help="Exclude items from generation.",
)
@click.option("-s", "--single", is_flag=True, help="Generate output as a single file.")
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
@click.option(
    "--list",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=print_supported_devices,
    help="Show list of the supported devices and exit.",
)
@click.version_option()
def cli(svd, output, language, template, mapping, exclude, single, white_list, black_list):  # type: ignore[no-untyped-def] # noqa: C901
    """D-RAL - Device Register Access Layer

    Generate D-RAL files in the OUTPUT from SVD.

    \b
    SVD    - can be a path to external SVD file or name of the already supported device.
             Type 'dral --list' to see all supported devices.

    \b
    OUTPUT - is a path where files will be generated.
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

    exclude = exclude if exclude else []

    template_dir_list = [Utils.get_template_dir(language, Utils.get_device_template(svd))]
    if template:
        template_dir_list.insert(0, template)
    template_object = DralTemplate(template_dir_list)

    if mapping:
        with open(mapping, "r", encoding="utf-8") as mapping_file:
            mapping = yaml.load(mapping_file, Loader=yaml.FullLoader)

    info = "[bold green]Generating D-Ral files..."
    with console.status(info):
        # Convert data using adapter
        adapter = SvdAdapter(svd)
        device = adapter.convert()

        # Apply filters
        filters: Any = []
        if black_list is not None:
            filters.append(BlackListFilter(black_list))
        if white_list is not None:
            filters.append(WhiteListFilter(white_list))
        filters.append(BanksFilter())
        if exclude:
            filters.append(ExcludeFilter(exclude))
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

        chip = Utils.get_device_info(svd)[0]
        output_format: Any = CppFormat(output, "dral", chip)
        if language == "cpp":
            output_format = CppFormat(output, "dral", chip)
        elif language == "python":
            output_format = PythonFormat(output, chip)
        output_format.make(objects, model=dral_model_file, single=single)

    console.print(f"Successfully generated D-Ral files to {output}", style="green")


if __name__ == "__main__":
    cli()  # type: ignore[misc] # noqa
