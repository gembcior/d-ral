from ..types import Device
from .base import BaseFilter


class BlackListFilter(BaseFilter):
    def __init__(self, _list: Device) -> None:
        super().__init__()
        self._list = _list

    def apply(self, device: Device) -> Device:
        return device
