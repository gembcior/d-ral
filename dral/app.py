from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.traceback import install as traceback

from .adapter.svd import SvdAdapter
from .adapter.white_black_list import WhiteBlackListAdapter
from .filter import BanksFilter, BlackListFilter, WhiteListFilter
from .format import CMakeLibFormat, MbedAutomatifyFormat
from .generator import Generator
from .utils import Utils


def print_supported_devices(ctx: Any, param: Any, value: Any) -> None:
    del param
    if not value or ctx.resilient_parsing:
        return
    click.echo("TODO")
    ctx.exit()


def validate_svd(ctx: Any, param: Any, value: Any) -> Any:
    del ctx, param
    if Path(value).exists():
        return Path(value).resolve()
    value = Utils.get_svd_file(value)
    if value is not None:
        return value
    raise click.BadParameter("SVD must be a path to external SVD file or name of the already supported device")


@click.command()
@click.argument("svd", type=click.UNPROCESSED, callback=validate_svd)
@click.argument("output", type=click.Path(resolve_path=True, path_type=Path))
@click.option(
    "-t",
    "--template",
    default="dral",
    show_default=True,
    type=click.Choice(["dral", "mbedAutomatify"], case_sensitive=False),
    help="Specify template used to generate files.",
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
def cli(svd, output, template, exclude, single, white_list, black_list):  # type: ignore[no-untyped-def]
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
    adapter = SvdAdapter(svd)
    generator = Generator(template)

    info = "[bold green]Generating D-Ral files..."
    with console.status(info):
        # Convert data using adapter
        device = adapter.convert()

        # Apply filters
        filters: Any = []
        if black_list is not None:
            filters.append(BlackListFilter(black_list))
        if white_list is not None:
            filters.append(WhiteListFilter(white_list))
        filters.append(BanksFilter())
        for item in filters:
            device = item.apply(device)

        # Generate D-RAL data
        objects = generator.generate(device, exclude=exclude)

        # Make output
        output = output / "dralOutput"

        output_format: Any = CMakeLibFormat(output, "dral")
        if template == "dral":
            output_format = CMakeLibFormat(output, "dral")
        elif template == "mbedAutomatify":
            chip, family, brand = Utils.get_device_info(svd)
            output_format = MbedAutomatifyFormat(output, chip, family, brand)
        output_format.make(objects, single)

    console.print(f"Successfully generated D-Ral files to {output}", style="green")


if __name__ == "__main__":
    cli()  # noqa
