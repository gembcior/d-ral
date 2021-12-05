from .base import BaseAdapter
import svd2py


class SvdAdapter(BaseAdapter):
    def __init__(self, svd_file):
        self._svd_file = svd_file

    # TODO split into smaller functions
    def _svd_to_dral(self, svd):
        device = svd["device"]
        data = {
            "device": {
                "name": device["name"],
                "description": device["description"],
                "peripherals": []
            }
        }
        peripherals_list = []
        for peripheral in device["peripherals"]:
            new_peripheral = {
                "name": peripheral["name"],
                "description": peripheral["description"],
                "address": peripheral["baseAddress"],
                "registers": []
            }
            registers_list = []
            for register in peripheral["registers"]["register"]:
                new_register = {
                    "name": register["name"],
                    "description": register["description"],
                    "offset": register["addressOffset"],
                    "size": register["size"],
                    "access": register["access"] if "access" in register else "",
                    "resetValue": register["resetValue"],
                    "fields": []
                }
                fields_list = []
                for field in register["fields"]:
                    new_field = {
                        "name": field["name"],
                        "description": field["description"],
                        "position": field["bitOffset"],
                        "mask": ((1 << field["bitWidth"]) - 1),
                        "width": field["bitWidth"]
                    }
                    fields_list.append(new_field)
                new_register["fields"] = fields_list
                registers_list.append(new_register)
            new_peripheral["registers"] = registers_list
            peripherals_list.append(new_peripheral)
        data["device"]["peripherals"] = peripherals_list
        return data

    def convert(self):
        svd = svd2py.SvdParser(self._svd_file)
        svd = svd.convert()
        return self._svd_to_dral(svd)

