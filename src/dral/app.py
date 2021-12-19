from rich.traceback import install as traceback
from rich.console import Console
from .generator import Generator
from .adapter.svd import SvdAdapter
from .format import SingleFileFormat
from .format import CMakeLibFormat
from pathlib import Path
import importlib.resources as resources
import argparse
import sys
import re
import os


def get_svd_file(brand, chip):
    with resources.path("dral.devices.%s" % brand, "%s.svd" % chip) as svd:
        return Path(svd)


def main():
    traceback()
    console = Console()

    description = "D-RAL - Device Register Access Layer"
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

    arg_help = (
        "SVD file from which files will be generated.\n"
        "Can be a path to SVD file with .svd extension or string with special format pointing to internal SVD files.\n"
        "\n"
        "Supported formats:\n"
        "- \"B.F.C\"\n"
        "- \"B.C\"\n"
        "\n"
        "Where:\n"
        "B - brand\n"
        "F - family\n"
        "C - chip\n"
        "\n"
        "Example: stm32.f4.stm32f411, rpi.rp2040"
    )

    parser.add_argument("svd", help=arg_help)

    parser.add_argument("output", help="Path where files will be generated.")

    parser.add_argument("-t", "--template", default="default",
                        help="Specify template used to generate files.")

    parser.add_argument("-e", "--exclude", action="extend", nargs="+", type=str,
                        help="Exclude items from generation.")

    parser.add_argument("-f", "--format", default="cmake",
                        help="Output format.")

    args = parser.parse_args()

    pattern = [
        re.compile("^(\/*.+)\.svd$"),
        re.compile("^([a-zA-Z0-9]+\.?){1}[a-zA-Z0-9]+$"),
        re.compile("^([a-zA-Z0-9]+\.?){2}[a-zA-Z0-9]+$"),
    ]
    if re.search(pattern[0], args.svd) is not None:
        svd_path = Path(args.svd).expanduser().resolve()
    elif re.search(pattern[1], args.svd) is not None:
        svd = args.svd.split(".")
        svd_path = get_svd_file(svd[0], svd[1])
    elif re.search(pattern[2], args.svd) is not None:
        svd = args.svd.split(".")
        svd_path = get_svd_file("%s.%s" % (svd[0], svd[1]), svd[2])
    else:
        console.print("ERROR: Invalid svd argument format!\n")
        parser.print_help()
        sys.exit()

    exclude = args.exclude if args.exclude else []
    output = Path(args.output).expanduser().resolve()
    adapter = SvdAdapter(svd_path)
    template = args.template
    generator = Generator(adapter, template=template)

    info = "[bold green]Generating D-Ral files..."
    with console.status(info):
        objects = generator.generate(exclude=exclude)
        if args.format == "cmake":
            output_format = CMakeLibFormat(output, "dral")
        elif args.format == "single":
            output_format = SingleFileFormat(output, "dral.h")
        else:
            output_format = CMakeLibFormat(output, "dral")
        output_format.make(objects)

    console.print("Successfully generated D-Ral files to %s" % os.path.abspath(args.output), style="green")


if __name__ == "__main__":
    main()
