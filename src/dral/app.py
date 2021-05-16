from rich.traceback import install as traceback
from rich.console import Console
from rich import print
from .generator import Generator
import importlib.resources as resources
import argparse
import sys
import re
import os


def get_svd_file(brand, chip):
    with resources.path("dral.devices.%s" % brand, "%s.svd" % chip) as svd:
        return svd


def main():
    traceback()

    description = "D-RAL - Device Register Abstraction Layer"
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

    args = parser.parse_args()

    pattern = [
        re.compile("^(\/*.+)\.svd$"),
        re.compile("^([a-zA-Z0-9]+\.?){1}[a-zA-Z0-9]+$"),
        re.compile("^([a-zA-Z0-9]+\.?){2}[a-zA-Z0-9]+$"),
    ]
    if re.search(pattern[0], args.svd) is not None:
        svd_path = os.path.abspath(args.svd)
    elif re.search(pattern[1], args.svd) is not None:
        svd = args.svd.split(".")
        svd_path = get_svd_file(svd[0], svd[1])
    elif re.search(pattern[2], args.svd) is not None:
        svd = args.svd.split(".")
        svd_path = get_svd_file("%s.%s" % (svd[0], svd[1]), svd[2])
    else:
        print("ERROR: Invalid svd argument format!\n")
        parser.print_help()
        sys.exit()

    console = Console()
    info = "[bold green]Generating D-Ral files..."
    with console.status(info) as status:
        generator = Generator(svd_path)
        generator.generate(os.path.abspath(args.output))
    console.print("Successfully generated D-Ral files to %s" % os.path.abspath(args.output), style="green")

if __name__ == "__main__":
    main()
