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

from __future__ import annotations

import subprocess

from dral.core.generator import DralOutputFile
from dral.formatter.base import DralFormatter


class PythonFormatter(DralFormatter):
    def format(self, objects: DralOutputFile | list[DralOutputFile]) -> list[DralOutputFile]:
        if isinstance(objects, DralOutputFile):
            objects = [objects]
        for i, item in enumerate(objects):
            result = subprocess.run(
                ["ruff", "--config", str(self._get_style_dir() / "ruff.toml"), "format", "-"], check=False, input=item.content, text=True, capture_output=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"Formatting failed for {item.name}: {result.stderr}")
            objects[i] = DralOutputFile(item.name, result.stdout)
        return objects
