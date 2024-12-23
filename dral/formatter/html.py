from __future__ import annotations

from dral.core.generator import DralOutputFile
from dral.formatter.base import DralFormatter


class HtmlFormatter(DralFormatter):
    def format(self, objects: DralOutputFile | list[DralOutputFile]) -> list[DralOutputFile]:
        if isinstance(objects, DralOutputFile):
            return [objects]
        return objects
