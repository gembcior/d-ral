from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

from .mapping import DralMapping
from .template import DralTemplate
from .types import Bank, Device, Field, Peripheral, Register


class DralPatternInvalid(Exception):
    def __init__(self, *args: Any) -> None:
        super().__init__(args)


MappingType = Dict[str, Dict[str, Union[str, List[str]]]]


class DralObject(ABC):
    def __init__(
        self,
        root: Union[Device, Peripheral, Register, Field],
        mapping: DralMapping,
        template: DralTemplate,
        exclude: Union[None, List[str]] = None,
    ):
        super().__init__()
        self._children: Dict[str, List[Union[DralPeripheral, DralRegister, DralBank, DralField]]] = {}
        if exclude is None:
            exclude = []
        self._exclude = exclude
        self._root = root
        self._template = template
        self._template_file: Dict[str, str] = {}
        self._mapping = mapping

    def _get_mapping(self) -> MappingType:
        return {
            "default": {"name": self._root.name, "description": self._root.description},
            "simple": {"name": self._root.name, "description": self._root.description},
        }

    def _get_children_content(self, _type: str, variant: str = "default") -> List[str]:
        content: List[str] = []
        try:
            for item in self._children[_type]:
                content = content + item.parse(variant)
        except KeyError:
            # Raise an exception
            # Key not supported
            # Exit or just warrning
            pass
        return content

    def _add_children(self, _type: str, element: Union[DralPeripheral, DralRegister, DralField]) -> None:
        try:
            self._children[_type].append(element)
        except KeyError:
            self._children.update({_type: [element]})

    @abstractmethod
    def parse(self, variant: str = "default") -> List[str]:
        pass


class DralDevice(DralObject):
    def __init__(self, root: Device, mapping: DralMapping, template: DralTemplate, exclude: Union[None, List[str]] = None):
        super().__init__(root, mapping, template, exclude)
        self._root = root

    def __str__(self) -> str:
        return "device"

    def parse(self, variant: str = "default") -> List[Dict[str, str]]:  # type: ignore[override]
        if "peripherals" not in self._exclude:
            for item in self._root.peripherals:  # type: ignore[union-attr]
                peripheral = DralPeripheral(item, self._mapping, self._template, exclude=self._exclude)
                self._add_children("peripherals", peripheral)

        mapping = self._get_mapping()
        # mapping.update(self._mapping.get(self._root))
        content = []
        for child in self._children["peripherals"]:
            string = self._template.replace_in_text(child.parse(variant), "device", mapping)
            content.append({"name": child._root.name, "content": "".join(string)})
        return content


class DralPeripheral(DralObject):
    def __init__(self, root: Peripheral, mapping: DralMapping, template: DralTemplate, exclude: Union[None, List[str]] = None):
        super().__init__(root, mapping, template, exclude)
        self._root = root
        self._template_file = {
            "default": "peripheral.dral",
            "simple": "peripheral.dral",
        }

    def __str__(self) -> str:
        return "peripheral"

    def _get_mapping(self) -> MappingType:
        mapping = super()._get_mapping()
        # TODO find better way how to update dict
        mapping["default"].update(
            {
                "address": f"0x{self._root.address:08X}",
                "registers": self._get_children_content("registers"),
                "banks": self._get_children_content("banks"),
            },
        )
        mapping["simple"].update(
            {
                "address": f"0x{self._root.address:08X}",
                "registers": self._get_children_content("registers", variant="simple"),
                "banks": self._get_children_content("banks", variant="simple"),
            },
        )
        return mapping

    def parse(self, variant: str = "default") -> List[str]:
        if "registers" not in self._exclude:
            for item in self._root.registers:  # type: ignore[union-attr]
                register = DralRegister(item, self._mapping, self._template, exclude=self._exclude)
                self._add_children("registers", register)
        if "banks" not in self._exclude:
            for item in self._root.banks:  # type: ignore[union-attr]
                register = DralBank(item, self._mapping, self._template, exclude=self._exclude)
                self._add_children("banks", register)
        mapping = self._get_mapping()
        # TODO add if guard
        # mapping.update(self._mapping.get(self._root))
        content = self._template.replace(self._template_file[variant], "peripheral", mapping)
        return content


class DralRegister(DralObject):
    def __init__(self, root: Register, mapping: DralMapping, template: DralTemplate, exclude: Union[None, List[str]] = None):
        super().__init__(root, mapping, template, exclude)
        self._root = root
        self._template_file = {
            "default": "register.dral",
            "simple": "register.simple.dral",
        }

    def __str__(self) -> str:
        return "register"

    def _get_mapping(self) -> MappingType:
        mapping = super()._get_mapping()
        mapping["default"].update(
            {
                "offset": f"0x{self._root.offset:04X}",
                "size": f"{self._root.size}",
                "access": f"{self._root.access}",
                "reset_value": f"0x{self._root.reset_value:08X}",
                "fields": self._get_children_content("fields"),
            }
        )
        mapping["simple"].update(
            {
                "offset": f"0x{self._root.offset:04X}",
                "size": f"{self._root.size}",
                "access": f"{self._root.access}",
                "reset_value": f"0x{self._root.reset_value:08X}",
                "fields": self._get_children_content("fields", variant="simple"),
            }
        )
        return mapping

    def parse(self, variant: str = "default") -> List[str]:
        if "fields" not in self._exclude:
            for item in self._root.fields:  # type: ignore[union-attr]
                field = DralField(item, self._mapping, self._template, exclude=self._exclude)
                self._add_children("fields", field)
        mapping = self._get_mapping()
        # TODO add if guard
        # mapping.update(self._mapping.get(self._root))
        content = self._template.replace(self._template_file[variant], "register", mapping)
        return content


class DralBank(DralRegister):
    def __init__(self, root: Bank, mapping: DralMapping, template: DralTemplate, exclude: Union[None, List[str]] = None):
        super().__init__(root, mapping, template, exclude=exclude)
        self._root = root
        self._template_file = {
            "default": "bank.dral",
            "simple": "bank.dral",
        }

    def __str__(self) -> str:
        return "bank"

    def _get_mapping(self) -> MappingType:
        mapping = super()._get_mapping()
        mapping["default"].update(
            {"bankOffset": f"0x{self._root.bank_offset:04X}"},
        )
        mapping["simple"].update(
            {"bankOffset": f"0x{self._root.bank_offset:04X}"},
        )
        return mapping

    def parse(self, variant: str = "default") -> List[str]:
        if "fields" not in self._exclude:
            for item in self._root.fields:  # type: ignore[union-attr]
                field = DralBankField(item, self._mapping, self._template, exclude=self._exclude)
                self._add_children("fields", field)
        mapping = self._get_mapping()
        # TODO add if guard
        # mapping.update(self._mapping.get(self._root))
        content = self._template.replace(self._template_file[variant], "bank", mapping)
        return content


class DralField(DralObject):
    def __init__(self, root: Field, mapping: DralMapping, template: DralTemplate, exclude: Union[None, List[str]] = None):
        super().__init__(root, mapping, template, exclude)
        self._root = root
        self._template_file = {
            "default": "field.dral",
            "simple": "field.dral",
        }

    def __str__(self) -> str:
        return "field"

    def _get_mapping(self) -> MappingType:
        mapping = super()._get_mapping()
        mapping["default"].update(
            {"position": f"{self._root.position}", "mask": f"0x{self._root.mask:08X}", "width": f"{self._root.width}"},
        )
        mapping["simple"].update(
            {"position": f"{self._root.position}", "mask": f"0x{self._root.mask:08X}", "width": f"{self._root.width}"},
        )
        return mapping

    def parse(self, variant: str = "default") -> List[str]:
        mapping = self._get_mapping()
        # TODO add if guard
        # mapping.update(self._mapping.get(self._root))
        content = self._template.replace(self._template_file[variant], "field", mapping)
        return content


class DralBankField(DralField):
    def __init__(self, root: Field, mapping: DralMapping, template: DralTemplate, exclude: Union[None, List[str]] = None):
        super().__init__(root, mapping, template, exclude)
        self._template_file = {
            "default": "bank.field.dral",
            "simple": "bank.field.dral",
        }
