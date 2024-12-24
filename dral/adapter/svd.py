from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import svd2py

from dral.core.objects import (
    DralAccessType,
    DralDevice,
    DralField,
    DralGroup,
    DralGroupInstance,
    DralRegister,
)

from .base import BaseAdapter


class IncorrectSvdError(Exception):
    def __init__(self, message: str, dral_object: dict[str, Any] = {}):
        self.message = message
        self.dral_object = dral_object
        super().__init__(message, dral_object)


class SvdAdapter(BaseAdapter):
    def _get_missing_atribute(self, svd_object: dict[str, Any], svd_parent: dict[str, Any], attribute: str) -> Any:
        if attribute in svd_object:
            return None
        if attribute not in svd_parent:
            return None
        return svd_parent[attribute]

    def _get_missing_attributes_from_parent(self, svd_object: dict[str, Any], svd_parent: dict[str, Any], attributes: list[str]) -> dict[str, Any]:
        for attribute in attributes:
            missing = self._get_missing_atribute(svd_object, svd_parent, attribute)
            if missing is not None:
                svd_object[attribute] = self._get_missing_atribute(svd_object, svd_parent, attribute)
        return svd_object

    def _get_the_origin(self, svd_scope: list[dict[str, Any]], svd_element: dict[str, Any], derived_from: str) -> dict[str, Any]:
        if len(derived_from.split(".")) > 1:
            raise NotImplementedError("Resolving derivedFrom attribute from another scope is not supported yet.")
        for element in svd_scope:
            if element["name"] == derived_from:
                return element | svd_element
        return svd_element

    def _resolve_dim_groups(self, _: dict[str, Any]) -> list[dict[str, Any]]:
        raise NotImplementedError("The dimElementGroup element is not supported yet.")

    def _get_access_type(self, access: str) -> DralAccessType:
        mapping = {
            "read-only": DralAccessType.ReadOnly,
            "write-only": DralAccessType.WriteOnly,
            "read-write": DralAccessType.ReadWrite,
        }
        if access not in mapping:
            raise IncorrectSvdError(f"Unknown access type: {access}")
        return mapping[access]

    # TODO: Determine the value type from the description file.
    # NOTE: Is it a proper way to handle the defaults? (access)
    def _parse_fields(self, svd_fields: list[dict[str, Any]], svd_parent: dict[str, Any]) -> list[DralField]:
        fields = []
        for field in svd_fields:
            if "attributes" in field and "derivedFrom" in field["attributes"]:
                field = self._get_the_origin(svd_fields, field, field["attributes"]["derivedFrom"])
            if "bitRange" in field:
                pattern = re.compile(r"(\d+):(\d+)")
                result = re.search(pattern, field["bitRange"])
                if result is None:
                    raise IncorrectSvdError("Determining the position and width of the field is impossible.", field)
                position = int(result.group(2))
                width = (int(result.group(1)) + 1) - position
            elif "lsb" in field and "msb" in field:
                position = field["lsb"]
                width = (field["msb"] + 1) - position
            elif "bitOffset" in field and "bitWidth" in field:
                position = field["bitOffset"]
                width = field["bitWidth"]
            else:
                raise IncorrectSvdError("Determining the position and width of the field is impossible.", field)
            field = self._get_missing_attributes_from_parent(field, svd_parent, ["access"])
            new_field = DralField(
                name=field["name"],
                description=field["description"],
                value_type="uint32_t",
                position=position,
                width=width,
                access=self._get_access_type(field["access"]) if "access" in field else DralAccessType.ReadWrite,
            )
            fields.append(new_field)
        return fields

    def _parse_clusters(self, svd_clusters: list[dict[str, Any]], svd_parent: dict[str, Any]) -> list[DralGroup]:
        groups = []
        for cluster in svd_clusters:
            if "dim" in cluster:
                self._resolve_dim_groups(cluster)
            if "attributes" in cluster and "derivedFrom" in cluster["attributes"]:
                cluster = self._get_the_origin(svd_clusters, cluster, cluster["attributes"]["derivedFrom"])
            cluster = self._get_missing_attributes_from_parent(cluster, svd_parent, ["size", "resetValue", "access"])
            group = DralGroup(
                name=cluster["name"],
                description=cluster["description"] if "description" in cluster else "",
                address=cluster["addressOffset"],
                offset=0x0,
                groups=self._parse_clusters(cluster["cluster"], cluster) if "cluster" in cluster else [],
                registers=self._parse_registers(cluster["register"], cluster) if "register" in cluster else [],
                instances=[DralGroupInstance(cluster["name"], cluster["addressOffset"])],
            )
            groups.append(group)
        return groups

    # TODO: Determine the value type from the description file.
    # NOTE: Is it a proper way to handle the defaults? (access, resetValue)
    def _parse_registers(self, svd_registers: list[dict[str, Any]], svd_parent: dict[str, Any]) -> list[DralRegister]:
        registers = []
        for register in svd_registers:
            if "dim" in register:
                self._resolve_dim_groups(register)
            if "attributes" in register and "derivedFrom" in register["attributes"]:
                register = self._get_the_origin(svd_registers, register, register["attributes"]["derivedFrom"])
            register = self._get_missing_attributes_from_parent(register, svd_parent, ["size", "resetValue", "access"])
            new_register = DralRegister(
                name=register["name"],
                description=register["description"],
                access=self._get_access_type(register["access"]) if "access" in register else DralAccessType.ReadWrite,
                value_type="uint32_t",
                address=register["addressOffset"],
                size=register["size"],
                reset_value=register["resetValue"] if "resetValue" in register else 0,
                fields=self._parse_fields(register["fields"]["field"], register) if "fields" in register else [],
            )
            registers.append(new_register)
        return registers

    def _parse_peripherals(self, svd_peripherals: list[dict[str, Any]], svd_parent: dict[str, Any]) -> list[DralGroup]:
        groups = []
        for peripheral in svd_peripherals:
            if "dim" in peripheral:
                self._resolve_dim_groups(peripheral)
            if "attributes" in peripheral and "derivedFrom" in peripheral["attributes"]:
                peripheral = self._get_the_origin(svd_peripherals, peripheral, peripheral["attributes"]["derivedFrom"])
            peripheral = self._get_missing_attributes_from_parent(peripheral, svd_parent, ["size", "resetValue", "access"])
            group = DralGroup(
                name=peripheral["name"],
                description=peripheral["description"] if "description" in peripheral else "",
                address=peripheral["baseAddress"],
                offset=0x0,
                groups=(
                    self._parse_clusters(peripheral["registers"]["cluster"], peripheral)
                    if "registers" in peripheral and "cluster" in peripheral["registers"]
                    else []
                ),
                registers=self._parse_registers(peripheral["registers"]["register"], peripheral) if "registers" in peripheral else [],
                instances=[DralGroupInstance(peripheral["name"], peripheral["baseAddress"])],
            )
            groups.append(group)
        return groups

    def _svd_to_dral(self, svd: dict[str, Any]) -> DralDevice:
        svd_device = svd["device"]
        device = DralDevice(
            name=svd_device["name"],
            description=svd_device["description"],
            groups=self._parse_peripherals(svd_device["peripherals"]["peripheral"], svd_device),
        )
        return device

    def convert(self, input_file: Path) -> DralDevice:
        svd = svd2py.SvdParser()
        svd = svd.convert(input_file)
        return self._svd_to_dral(svd)
