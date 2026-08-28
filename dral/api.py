# =================================================================================
#
# MIT License
#
# Copyright (c) 2026 Gembcior
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# =================================================================================

"""Library entry point for programmatic (non-CLI) use of D-RAL.

Wraps the same parse -> generate -> save pipeline the `dral` CLI uses
(see dral/app.py), for callers that want generated files without shelling
out to a subprocess.
"""

from __future__ import annotations

from pathlib import Path

from dral.core import factory


def generate_python(input_file: Path, output_path: Path, adapter: str = "svd", skip_groups_detection: bool = False) -> str:
    """Generate D-RAL python module(s) from a device description file.

    Output is written to `output_path/dralOutput/python/<device.name>/`
    (an `__init__.py` plus one file per top-level group).

    Args:
        input_file: path to the device description file (SVD or D-RAL YAML).
        output_path: directory under which `dralOutput/python/...` is created.
        adapter: "svd" or "dral" (native YAML), matching the `dral` CLI's `-a` option.
        skip_groups_detection: matches the CLI's `-s` flag.

    Returns:
        The parsed device name, i.e. the subdirectory name under
        `dralOutput/python/` where the generated files were written.
    """
    options = factory.DralAppOptions(
        input_file=input_file,
        output_path=output_path,
        language="python",
        adapter=adapter,
        access_type="direct",
        template_path=None,
        skip_groups_detection=skip_groups_detection,
        skip_output_formatting=True,  # avoid the `ruff format` subprocess, not needed for correctness
        white_list=None,
        black_list=None,
    )
    context = factory.get_python_context(options)

    device = context.parse(options.input_file)
    files = context.generate(device)
    context.save(files, device.name)

    return device.name
