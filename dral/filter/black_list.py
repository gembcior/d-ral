from __future__ import annotations

from dral.core.objects import DralDevice
from dral.filter.base import BaseFilter


class BlackListFilter(BaseFilter):
    def __init__(self, _list: DralDevice) -> None:
        super().__init__()
        self._list = _list

    def apply(self, device: DralDevice) -> DralDevice:
        _ = device
        raise NotImplementedError("Black List filtering not implemented yet")
