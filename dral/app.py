from __future__ import annotations

from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.traceback import install as traceback

import dral.core.factory as factory
from dral.adapter.base import BaseAdapter


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
    type=click.Choice(["cpp", "html"], case_sensitive=False),
    help="Specify the programming language for which you want to generate files.",
)
@click.option(
    "-t",
    "--access-type",
    default="direct",
    show_default=True,
    type=click.Choice(["direct", "indirect"], case_sensitive=False),
    help="Specify the access template. Applys only for C++ model.",
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
def cli(**kwargs: dict[str, Any]) -> None:
    """D-RAL - Device Register Access Layer

    Generate D-RAL files from INPUT-FILE.

    \b
    INPUT-FILE  - path to device description file.
    """
    traceback()
    console = Console()
    options = factory.DralAppOptions(**kwargs)  # type: ignore[arg-type]

    info = "[bold yellow]Working..."
    with console.status(info):
        console.print("Preparing environment...")
        context = factory.get_context(options)

        console.print("Parsing device description file...")
        device = context.parse(options.input_file)

        console.print("Generating D-RAL content...")
        dral_output_files = context.generate(device)
        if not isinstance(dral_output_files, list):
            dral_output_files = [dral_output_files]

        if not options.skip_output_formatting:
            console.print("Formatting D-RAL content...")
            dral_output_files = context.format(dral_output_files)

        console.print("Saving D-RAL content to files...")
        context.save(dral_output_files, device.name)

    console.print(f"Successfully generated D-RAL files to {options.output_path}", style="green")


def with_custom_adapter(adapter: type[BaseAdapter]) -> None:
    factory.override_adapter(adapter)
    cli()


if __name__ == "__main__":
    cli()
