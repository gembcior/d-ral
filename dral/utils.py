from __future__ import annotations

import glob
from importlib import resources
from pathlib import Path
from typing import Optional, Tuple, Union


class Utils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_template(template: Union[str, Path], name: str) -> Path:
        if isinstance(template, Path):
            return template / name
        else:
            with resources.path(f"dral.templates.{template}", name) as item:
                return Path(item)

    @staticmethod
    def get_template_dir(name: str) -> Path:
        templates_path = Path(__file__).parent / "templates"
        return templates_path / name

    @staticmethod
    def get_svd_file(device: str) -> Optional[Path]:
        devices_path = Path(__file__).parent / "devices"
        svd = glob.glob(f"{devices_path}/**/{device}.svd", recursive=True)
        if svd:
            return devices_path / Path(svd[0])
        return None

    @staticmethod
    def get_device_info(svd: Path) -> Tuple[str, str, str]:
        devices_path = Path(__file__).parent / "devices"
        svd = svd.resolve().relative_to(devices_path)
        device_info = svd.parts
        if len(device_info) > 2:
            return svd.stem, device_info[1], device_info[0]
        return svd.stem, "", device_info[0]

    @staticmethod
    def get_mapping_file(name: str) -> Path:
        with resources.path("dral.mappings", name) as item:
            return Path(item)
