from __future__ import annotations

import tarfile
import urllib.request
from pathlib import Path


class Utils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_template_dir(language: str) -> Path:
        templates_path = Path(__file__).parent.parent / "templates" / language
        return templates_path

    @staticmethod
    def get_forbidden_words(language: str) -> list[str]:
        forbidden_words_path = Path(__file__).parent.parent / "forbidden"
        if not forbidden_words_path.exists():
            raise FileNotFoundError(f"Forbidden words files directory not found at {forbidden_words_path}")
        output = []
        for words_file in forbidden_words_path.glob("model.txt"):
            with open(words_file, encoding="UTF-8") as f:
                output.extend([word.strip().lower() for word in f.readlines() if not word.strip().startswith("#")])
        for words_file in forbidden_words_path.glob(f"{language}.txt"):
            with open(words_file, encoding="UTF-8") as f:
                output.extend([word.strip().lower() for word in f.readlines() if not word.strip().startswith("#")])
        return output

    @staticmethod
    def get_model_release(output: Path) -> None:
        version = "v0.2.0"
        url = f"https://github.com/gembcior/d-ral-model/releases/download/{version}/d-ral-model.tar.gz"
        response = urllib.request.urlopen(url)
        package = output / "d-ral-model.tar.gz"
        with open(package, "wb") as f:
            f.write(response.read())
        with tarfile.open(package, "r") as tar:
            tar.extractall(output)
        package.unlink()
