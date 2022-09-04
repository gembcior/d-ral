import glob
import importlib.resources as resources
from pathlib import Path
from typing import Optional, Tuple


class Utils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_template(template: str, name: str) -> Path:
        with resources.path("dral.templates.%s" % template, name) as item:
            return Path(item)

    @staticmethod
    def get_svd_file(device: str) -> Optional[Path]:
        devices_path = str(resources.files("dral.devices"))
        svd = glob.glob(f"**/{device}.svd", root_dir=devices_path, recursive=True)
        if svd:
            return devices_path / Path(svd[0])
        else:
            return None

    @staticmethod
    def get_device_info(svd: Path) -> Tuple:
        devices_path = str(resources.files("dral.devices"))
        svd = svd.resolve().relative_to(devices_path)
        device_info = svd.parts
        if len(device_info) > 2:
            return svd.stem, device_info[1], device_info[0]
        else:
            return svd.stem, "", device_info[0]
