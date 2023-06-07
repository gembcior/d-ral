from __future__ import annotations

from typing import List

from ..types import Device
from .base import BaseFilter


class ExcludeFilter(BaseFilter):
    def __init__(self, exclude: List[str]) -> None:
        self._exclude = exclude

    def apply(self, device: Device) -> Device:
        return device
