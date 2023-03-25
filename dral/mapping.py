from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union

import yaml

from .utils import Utils

MappingType = Dict[str, Dict[str, Dict[str, Union[str, List[str]]]]]


class DralMapping:
    def __init__(self, mapping: Union[str, Path]):
        if isinstance(mapping, Path):
            mapping_file = mapping
        else:
            mapping_file = Utils.get_mapping_file(f"{mapping}.yaml")
        with open(mapping_file, "r", encoding="UTF-8") as file:
            self._mapping = yaml.load(file, Loader=yaml.FullLoader)

    def get(self) -> MappingType:
        output = {}
        for _object, attr in self._mapping.items():
            output.update(
                {
                    _object: {
                        "default": attr,
                        "simple": attr,
                    },
                }
            )

        return output
