from abc import ABC, abstractmethod

from ..types import Device


class BaseFilter(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def apply(self, device: Device) -> Device:
        pass
