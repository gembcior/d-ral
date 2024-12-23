from __future__ import annotations

import subprocess
import tempfile

from dral.core.generator import DralOutputFile
from dral.formatter.base import DralFormatter


class CppFormatter(DralFormatter):
    def format(self, objects: DralOutputFile | list[DralOutputFile]) -> list[DralOutputFile]:
        if isinstance(objects, DralOutputFile):
            objects = [objects]
        for i, item in enumerate(objects):
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as temp:
                temp.write(item.content)
                temp.flush()
                result = subprocess.run(
                    f"cat {temp.name} | clang-format -style=file:{self._get_style_dir() / '.clang-format'}", shell=True, capture_output=True
                )
            objects[i] = DralOutputFile(item.name, result.stdout.decode("utf-8"))
        return objects
