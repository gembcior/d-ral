from dral.core.objects import DralDevice

from .base import BaseFilter


class FilterSupervisor:
    def __init__(self, filters: list[BaseFilter] | None = None):
        if filters is None:
            filters = []
        self._filters = filters

    def add(self, filter: BaseFilter) -> None:
        self._filters.append(filter)

    def apply(self, device: DralDevice) -> DralDevice:
        for item in self._filters:
            device = item.apply(device)
        return device
