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
    def get_template_dir(language: str, name: str) -> Path:
        templates_path = Path(__file__).parent / "templates" / language
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
        svd = svd.resolve()
        return svd.stem, "", ""

    @staticmethod
    def get_model_dir(language: str) -> Path:
        model_path = Path(__file__).parent / "templates" / "model" / language
        return model_path
