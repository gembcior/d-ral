from __future__ import annotations

from ..types import Device
from .base import BaseFilter
from typing import List


class ExcludeFilter(BaseFilter):
    def __init__(self, exclude: List) -> None:
        self._exclude = exclude

    def apply(self, device: Device) -> Device:
        return device
