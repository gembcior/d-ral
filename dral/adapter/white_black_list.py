from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from dral.adapter.base import BaseAdapter
from dral.objects import DralDevice


class WhiteBlackListAdapter(BaseAdapter):
    def _list_to_dral(self, _list: dict[str, Any]) -> DralDevice:
        device = DralDevice(name="WhiteBlackList", **_list)
        return device

    def convert(self, input_file: Path) -> DralDevice:
        with open(input_file, "r", encoding="UTF-8") as f:
            _list = yaml.load(f, Loader=yaml.FullLoader)
        return self._list_to_dral(_list)
