from .objects import DralDevice
from pathlib import Path
import importlib.resources as resources
from .utils import Utils


class Generator:
    def __init__(self, adapter, template="default", template_path=None):
        self._adapter = adapter
        self._utils = Utils(template, template_path)

    def _get_register_model_content(self):
        model = self._utils.get_template("model.dral")
        with open(model, "r") as f:
            return f.read()

    def _white_list_filter(self, data, list):
        filtered_list = []
        for peripheral in list["peripherals"]:
            for item in data["device"]["peripherals"]:
                if item["name"] == peripheral["name"]:
                    if "registers" in peripheral:
                        new_peripheral = peripheral
                        for reg in peripheral["registers"]:
                            pass
                    else:
                        filtered_list.append(item)
        return filtered_list

    def _black_list_filter(self, data, list):
        pass

    def generate(self, exclude=[], white_list=[], black_list=[]):
        device = self._adapter.convert()
        # if white_list: 
        #     data["device"]["peripherals"] = self._white_list_filter(data, white_list)
        # if black_list:
        #     data["device"]["peripherals"] = self._black_list_filter(data, white_list)
        dral_device = DralDevice(device, utils=self._utils, exclude=exclude)
        objects = dral_device.parse()
        if self._utils.get_template("model.dral").exists():
            objects.append({"name": "register_model", "content": self._get_register_model_content()})
        return objects
