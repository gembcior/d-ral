from __future__ import annotations

from abc import ABC, abstractmethod

from dral.core.objects import DralDevice


class BaseFilter(ABC):
    @abstractmethod
    def apply(self, device: DralDevice) -> DralDevice:
        pass
