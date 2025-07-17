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
                ["ruff", "--config", str(self._get_style_dir() / "ruff.toml"), "format", "-"], input=item.content, text=True, capture_output=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"Formatting failed for {item.name}: {result.stderr}")
            objects[i] = DralOutputFile(item.name, result.stdout)
        return objects
