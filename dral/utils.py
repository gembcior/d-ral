from __future__ import annotations

from pathlib import Path


class Utils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_template_dir(language: str, name: str) -> Path:
        templates_path = Path(__file__).parent / "templates" / language
        return templates_path / name

    @staticmethod
    def get_forbidden_words(language: str) -> list[str]:
        forbidden_words_path = Path(__file__).parent / "forbidden"
        if not forbidden_words_path.exists():
            raise FileNotFoundError(f"Forbidden words files directory not found at {forbidden_words_path}")
        output = []
        for words_file in forbidden_words_path.glob("model.txt"):
            with open(words_file, "r", encoding="UTF-8") as f:
                output.extend([word.strip().lower() for word in f.readlines() if not word.strip().startswith("#")])
        for words_file in forbidden_words_path.glob(f"{language}.txt"):
            with open(words_file, "r", encoding="UTF-8") as f:
                output.extend([word.strip().lower() for word in f.readlines() if not word.strip().startswith("#")])
        return output

    @staticmethod
    def get_model_dir(language: str) -> Path:
        model_path = Path(__file__).parent / "model" / language
        return model_path
