from pathlib import Path
from typing import Any, Dict, Union

import yaml

from .types import DralBaseType
from .utils import Utils


class DralMapping:
    def __init__(self, mapping: Union[str, Path]):
        if isinstance(mapping, Path):
            mapping_file = mapping
        else:
            mapping_file = Utils.get_mapping_file(f"{mapping}.yaml")
        with open(mapping_file, "r", encoding="UTF-8") as file:
            self._mapping = yaml.load(file, Loader=yaml.FullLoader)

    def get(self, root: DralBaseType) -> Dict:
        mapping: Dict = self._mapping[str(root)]
        output = {}
        for attr, rules in mapping.items():
            try:
                value = getattr(root, attr)
            except AttributeError:
                continue
            output.update({attr: rules["value"].format(value)})
        return output
