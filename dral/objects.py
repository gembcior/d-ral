from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from .mapping import DralMapping, MappingType
from .template import DralTemplate
from .types import Bank, Device, Field, Peripheral, Register


class DralPatternInvalid(Exception):
    def __init__(self, *args: Any) -> None:
        super().__init__(args)


class DralObject(ABC):
    def __init__(
        self,
        root: Union[Device, Peripheral, Register, Field],
        template: DralTemplate,
        exclude: Union[None, List[str]] = None,
        mapping: Optional[DralMapping] = None,
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

    @abstractmethod
    def _get_mapping(self) -> MappingType:
        pass

    def _get_children_content(self, _type: str, variant: str = "default") -> List[str]:
        content: List[str] = []
        if _type not in self._children:
            # Raise an exception
            # Key not supported
            # Exit or just warrning
            return []
        for item in self._children[_type]:
            content = content + item.parse(variant)
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
    def __init__(self, root: Device, template: DralTemplate, exclude: Union[None, List[str]] = None, mapping: Optional[DralMapping] = None):
        super().__init__(root, template, exclude, mapping)
        self._root = root

    def __str__(self) -> str:
        return "device"

    def _get_mapping(self) -> MappingType:
        return {
            "device": {
                "default": {
                    "name": self._root.name,
                    "description": self._root.description,
                },
                "simple": {
                    "name": self._root.name,
                    "description": self._root.description,
                },
            }
        }

    def parse(self, variant: str = "default") -> List[Dict[str, str]]:  # type: ignore[override]
        if "peripherals" not in self._exclude:
            for item in self._root.peripherals:
                peripheral = DralPeripheral(item, self._template, exclude=self._exclude, mapping=self._mapping)
                self._add_children("peripherals", peripheral)

        content = []
        for child in self._children["peripherals"]:
            string = None
            if self._mapping is not None:
                mapping = self._mapping.get()
                string = self._template.replace(child.parse(variant), mapping)
            mapping = self._get_mapping()
            string = string if string is not None else child.parse(variant)
            string = self._template.replace(string, mapping)
            content.append({"name": child._root.name, "content": "".join(string)})
        return content


class DralPeripheral(DralObject):
    def __init__(self, root: Peripheral, template: DralTemplate, exclude: Union[None, List[str]] = None, mapping: Optional[DralMapping] = None):
        super().__init__(root, template, exclude, mapping)
        self._root = root
        self._template_file = {
            "default": "peripheral.dral",
            "simple": "peripheral.dral",
        }

    def __str__(self) -> str:
        return "peripheral"

    def _get_mapping(self) -> MappingType:
        return {
            "peripheral": {
                "default": {
                    "name": self._root.name,
                    "description": self._root.description,
                    "address": f"0x{self._root.address:08X}",
                    "registers": self._get_children_content("registers"),
                    "banks": self._get_children_content("banks"),
                },
                "simple": {
                    "name": self._root.name,
                    "description": self._root.description,
                    "address": f"0x{self._root.address:08X}",
                    "registers": self._get_children_content("registers", variant="simple"),
                    "banks": self._get_children_content("banks", variant="simple"),
                },
            }
        }

    def parse(self, variant: str = "default") -> List[str]:
        if "registers" not in self._exclude:
            for item in self._root.registers:
                register = DralRegister(item, self._template, exclude=self._exclude, mapping=self._mapping)
                self._add_children("registers", register)
        if "banks" not in self._exclude:
            for item in self._root.banks:
                register = DralBank(item, self._template, exclude=self._exclude, mapping=self._mapping)
                self._add_children("banks", register)
        content = None
        if self._mapping is not None:
            mapping = self._mapping.get()
            content = self._template.replace(self._template_file[variant], mapping)

        mapping = self._get_mapping()
        content = content if content is not None else self._template_file[variant]
        content = self._template.replace(content, mapping)
        return content


class DralRegister(DralObject):
    def __init__(self, root: Register, template: DralTemplate, exclude: Union[None, List[str]] = None, mapping: Optional[DralMapping] = None):
        super().__init__(root, template, exclude, mapping)
        self._root = root
        self._template_file = {
            "default": "register.dral",
            "simple": "register.simple.dral",
        }

    def __str__(self) -> str:
        return "register"

    def _get_mapping(self) -> MappingType:
        return {
            "register": {
                "default": {
                    "name": self._root.name,
                    "description": self._root.description,
                    "offset": f"0x{self._root.offset:04X}",
                    "size": f"{self._root.size}",
                    "access": f"{self._root.access}",
                    "reset_value": f"0x{self._root.reset_value:08X}",
                    "fields": self._get_children_content("fields"),
                },
                "simple": {
                    "name": self._root.name,
                    "description": self._root.description,
                    "offset": f"0x{self._root.offset:04X}",
                    "size": f"{self._root.size}",
                    "access": f"{self._root.access}",
                    "reset_value": f"0x{self._root.reset_value:08X}",
                    "fields": self._get_children_content("fields", variant="simple"),
                },
            }
        }

    def parse(self, variant: str = "default") -> List[str]:
        if "fields" not in self._exclude:
            for item in self._root.fields:
                field = DralField(item, self._template, exclude=self._exclude, mapping=self._mapping)
                self._add_children("fields", field)
        content = None
        if self._mapping is not None:
            mapping = self._mapping.get()
            content = self._template.replace(self._template_file[variant], mapping)

        mapping = self._get_mapping()
        content = content if content is not None else self._template_file[variant]
        content = self._template.replace(content, mapping)
        return content


class DralBank(DralRegister):
    def __init__(self, root: Bank, template: DralTemplate, exclude: Union[None, List[str]] = None, mapping: Optional[DralMapping] = None):
        super().__init__(root, template, exclude, mapping)
        self._root = root
        self._template_file = {
            "default": "bank.dral",
            "simple": "bank.dral",
        }

    def __str__(self) -> str:
        return "bank"

    def _get_mapping(self) -> MappingType:
        return {
            "bank": {
                "default": {
                    "name": self._root.name,
                    "description": self._root.description,
                    "offset": f"0x{self._root.offset:04X}",
                    "size": f"{self._root.size}",
                    "access": f"{self._root.access}",
                    "reset_value": f"0x{self._root.reset_value:08X}",
                    "fields": self._get_children_content("fields"),
                    "bankOffset": f"0x{self._root.bank_offset:04X}",
                },
                "simple": {
                    "name": self._root.name,
                    "description": self._root.description,
                    "offset": f"0x{self._root.offset:04X}",
                    "size": f"{self._root.size}",
                    "access": f"{self._root.access}",
                    "reset_value": f"0x{self._root.reset_value:08X}",
                    "fields": self._get_children_content("fields", variant="simple"),
                    "bankOffset": f"0x{self._root.bank_offset:04X}",
                },
            }
        }

    def parse(self, variant: str = "default") -> List[str]:
        if "fields" not in self._exclude:
            for item in self._root.fields:
                field = DralBankField(item, self._template, exclude=self._exclude, mapping=self._mapping)
                self._add_children("fields", field)
        content = None
        if self._mapping is not None:
            mapping = self._mapping.get()
            content = self._template.replace(self._template_file[variant], mapping)

        mapping = self._get_mapping()
        content = content if content is not None else self._template_file[variant]
        content = self._template.replace(content, mapping)
        return content


class DralField(DralObject):
    def __init__(self, root: Field, template: DralTemplate, exclude: Union[None, List[str]] = None, mapping: Optional[DralMapping] = None):
        super().__init__(root, template, exclude, mapping)
        self._root = root
        self._template_file = {
            "default": "field.dral",
            "simple": "field.dral",
        }

    def __str__(self) -> str:
        return "field"

    def _get_mapping(self) -> MappingType:
        return {
            "field": {
                "default": {
                    "name": self._root.name,
                    "description": self._root.description,
                    "position": f"{self._root.position}",
                    "mask": f"0x{self._root.mask:08X}",
                    "width": f"{self._root.width}",
                },
                "simple": {
                    "name": self._root.name,
                    "description": self._root.description,
                    "position": f"{self._root.position}",
                    "mask": f"0x{self._root.mask:08X}",
                    "width": f"{self._root.width}",
                },
            }
        }

    def parse(self, variant: str = "default") -> List[str]:
        content = None
        if self._mapping is not None:
            mapping = self._mapping.get()
            content = self._template.replace(self._template_file[variant], mapping)

        mapping = self._get_mapping()
        content = content if content is not None else self._template_file[variant]
        content = self._template.replace(content, mapping)
        return content


class DralBankField(DralField):
    def __init__(self, root: Field, template: DralTemplate, exclude: Union[None, List[str]] = None, mapping: Optional[DralMapping] = None):
        super().__init__(root, template, exclude, mapping)
        self._template_file = {
            "default": "bank.field.dral",
            "simple": "bank.field.dral",
        }
